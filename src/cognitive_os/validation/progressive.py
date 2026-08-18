"""渐进式验证(Progressive Validation)。

把验证从"搜索末端的一次性 Final Validation"转变为
"搜索过程中的 Continuous / Progressive Validation":
- 多轮证据累积(多网结果进入同一证据表);
- 置信度 = f(证据强度, 跨网共识, 观测轮数);
- **禁止硬性提前淘汰**: 低置信度候选只降权, 不进垃圾桶
  (对应 fix(validation): prevent premature candidate elimination);
- 早停: top-k 置信度稳定 / 达到阈值 / 预算用尽。
"""

from __future__ import annotations

from dataclasses import dataclass

from ..types import Evidence


@dataclass
class ValidatorConfig:
    confidence_threshold: float = 0.9  # 置信度达标即停
    stabilization_eps: float = 1e-3  # top-k 置信度均值稳定判据
    stabilize_rounds: int = 2  # 连续多少轮稳定才停
    max_rounds: int = 6  # 验证预算(防无限循环)
    consensus_w: float = 0.4  # 共识分量权重(1-consensus_w 为证据分量)
    aggregation: str = "max"  # 跨网/跨轮证据聚合: "max"(最强网主导) | "mean"(各网平均发言)


class ProgressiveValidator:
    """跨网、跨轮的渐进式验证器。"""

    def __init__(self, cfg: ValidatorConfig | None = None):
        self.cfg = cfg or ValidatorConfig()
        if self.cfg.aggregation not in ("max", "mean"):
            raise ValueError(f"aggregation 必须是 'max' 或 'mean', 收到 {self.cfg.aggregation!r}")
        self.evidence: dict[str, Evidence] = {}
        self._raw_scores: dict[str, list[float]] = {}
        self.rounds_run: int = 0
        self._topk_history: list[float] = []
        self._consecutive_stable: int = 0
        self.stopped_reason: str = ""

    def mark_round(self) -> None:
        """标记一轮验证的开始(每轮调用一次, 与网数无关)。"""
        self.rounds_run += 1

    def add_round(self, candidates: list[Evidence], net_name: str = "") -> None:
        """把一轮(一个网)的候选并入证据表。"""
        for ev in candidates:
            cur = self.evidence.get(ev.pid)
            if cur is None:
                self.evidence[ev.pid] = Evidence(pid=ev.pid)
                cur = self.evidence[ev.pid]
            # 证据分量: 始终记录原始观测(聚合方式在 update_confidence 统一决定)
            self._raw_scores.setdefault(ev.pid, []).append(ev.score)
            cur.semantic_sim = max(cur.semantic_sim, ev.semantic_sim)
            cur.source_evidence = max(cur.source_evidence, ev.source_evidence)
            cur.temporal_evidence = max(cur.temporal_evidence, ev.temporal_evidence)
            cur.structural_evidence = max(cur.structural_evidence, ev.structural_evidence)
            cur.votes += 1
            cur.rounds_seen = self.rounds_run

    def _aggregate_score(self, pid: str) -> float:
        """按配置聚合一个候选的跨网/跨轮证据分。"""
        scores = self._raw_scores.get(pid, [])
        if not scores:
            return self.evidence[pid].score
        if self.cfg.aggregation == "mean":
            return sum(scores) / len(scores)
        return max(scores)

    def update_confidence(self) -> None:
        """重算所有候选的置信度(证据强度 + 跨网共识)。"""
        max_votes = max((e.votes for e in self.evidence.values()), default=1)
        cw = self.cfg.consensus_w
        for e in self.evidence.values():
            e.score = self._aggregate_score(e.pid)
            consensus = e.votes / max_votes
            e.confidence = (1.0 - cw) * e.score + cw * consensus

    def top_k(self, k: int) -> list[str]:
        ranked = sorted(self.evidence.values(), key=lambda e: e.confidence, reverse=True)[:k]
        return [e.pid for e in ranked]

    def mean_topk_confidence(self, k: int) -> float:
        ranked = sorted(self.evidence.values(), key=lambda e: e.confidence, reverse=True)[:k]
        if not ranked:
            return 0.0
        return sum(e.confidence for e in ranked) / len(ranked)

    def should_stop(self, k: int) -> bool:
        """早停判定: 稳定 / 达标 / 预算用尽。"""
        cur = self.mean_topk_confidence(k)
        self._topk_history.append(cur)
        if len(self._topk_history) >= self.cfg.stabilize_rounds:
            window = self._topk_history[-self.cfg.stabilize_rounds :]
            stable = all(
                abs(window[i] - window[i + 1]) <= self.cfg.stabilization_eps
                for i in range(len(window) - 1)
            )
            self._consecutive_stable = self._consecutive_stable + 1 if stable else 0
        if self._consecutive_stable >= self.cfg.stabilize_rounds:
            self.stopped_reason = "stabilized"
            return True
        if cur >= self.cfg.confidence_threshold:
            self.stopped_reason = "threshold"
            return True
        if self.rounds_run >= self.cfg.max_rounds:
            self.stopped_reason = "budget"
            return True
        return False

    def final_ranked(self, k: int) -> list[str]:
        """最终排序(仍保留全部候选; 低置信度自然靠后, 不删除)。"""
        self.update_confidence()
        return self.top_k(k)
