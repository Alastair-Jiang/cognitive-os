"""Strategy C: Dynamic Multi-Net Retrieval(动态多网检索)。

流程(H-002 / RQ-1 / RQ-3):
1. 多个配置不同的检索网并行工作(不同半径/时间窗/来源权重/信号侧重);
2. 渐进式验证: 跨网证据合并 → 置信度更新 → 高置信候选成为下一轮
   扩张前沿(搜索空间随置信度动态调整);
3. 早停: top-k 置信度稳定 / 达标 / 预算用尽, 不必跑满固定预算;
4. 最终排序按置信度, 全程不硬性淘汰候选。
"""

from __future__ import annotations

import time

from ..nets.search_net import NetSearchStats, SearchNet, SearchNetConfig
from ..types import Query, RetrievalResult
from ..validation.progressive import ProgressiveValidator, ValidatorConfig
from .base import RetrievalStrategy


class DynamicMultiNetRetrieval(RetrievalStrategy):
    name = "C-multinet"

    def __init__(
        self,
        corpus,
        net_configs: list[SearchNetConfig],
        validator_cfg: ValidatorConfig | None = None,
        frontier_k: int | None = None,
    ):
        super().__init__(corpus)
        if not net_configs:
            raise ValueError("DynamicMultiNetRetrieval 需要至少一个 SearchNetConfig")
        self.nets = [SearchNet(corpus, cfg) for cfg in net_configs]
        self.validator_cfg = validator_cfg or ValidatorConfig()
        self.frontier_k = frontier_k

    def retrieve(self, query: Query, k: int) -> RetrievalResult:
        t0 = time.perf_counter()
        stats = NetSearchStats()
        q_emb = self.corpus.embed_seed(query.seed_pids)
        allowed = query.is_allowed

        validator = ProgressiveValidator(self.validator_cfg)
        frontier: list[str] = list(query.seed_pids)

        while True:
            validator.mark_round()
            for net in self.nets:
                candidates = net.search(
                    frontier,
                    q_emb,
                    extra_frontier=(),
                    stats=stats,
                    allowed=allowed,
                )
                validator.add_round(candidates, net.name)
            validator.update_confidence()
            if validator.should_stop(k):
                break
            frontier = validator.top_k(self.frontier_k or max(k, 5))
            if not frontier:
                break

        ranked = validator.final_ranked(k)
        scores = [validator.evidence[pid].confidence for pid in ranked]
        latency_ms = (time.perf_counter() - t0) * 1000.0
        return RetrievalResult(
            qid=query.qid,
            strategy=self.name,
            ranked_pids=ranked,
            scores=scores,
            evidence=validator.evidence,
            iterations=validator.rounds_run,
            similarity_calls=stats.similarity_calls,
            index_lookups=stats.index_lookups,
            latency_ms=latency_ms,
            early_stopped=validator.stopped_reason != "budget" and validator.rounds_run > 0,
            notes={
                "nets": [net.cfg.name for net in self.nets],
                "stopped_reason": validator.stopped_reason,
                "n_candidates": len(validator.evidence),
            },
        )
