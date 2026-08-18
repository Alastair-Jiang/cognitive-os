"""合成"信息空间"生成器(带 ground-truth 事件结构)。

设计目标(对应 BM-001):
1. 同事件碎片语义上更近, 但**不是平凡可分**: 事件共享潜在主题,
   产生跨事件语义重叠(即"苹果问题": 苹果新品/苹果财报/苹果产区灾害
   语义相似但属于不同信息结构);
2. 时间结构: 事件在时间窗内展开, 碎片带时间戳 → 支持"信息未完整"
   的截断实验;
3. 来源结构: 碎片来自不同来源, 来源有可靠性权重 → 锚点证据可超出
   纯语义(见 H-001 / H-003);
4. 完全可复现: 固定 seed, 纯标准库 random。
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from ..similarity import cosine, mean_embedding, normalize
from ..types import InformationPoint, Query, Embedding

Vector = Sequence[float]


@dataclass
class SyntheticCorpusConfig:
    n_events: int = 12
    fragments_per_event: int = 8
    embed_dim: int = 24
    n_topics: int = 5
    topics_per_event: int = 4  # 每个事件激活的主题数(跨事件重叠 → 歧义)
    within_event_noise: float = 0.5  # 碎片围绕事件主题的噪声幅度(默认档位: 高歧义)
    time_horizon: float = 100.0
    event_span: float = 20.0  # 事件展开的时间窗长度
    source_count: int = 4
    source_min_weight: float = 0.6
    primary_source_prob: float = 0.6  # 碎片使用事件主来源的概率
    index_top_m: int = 6  # 预计算邻居索引大小
    seed: int = 20260819


class SyntheticEventCorpus:
    """合成信息空间: 点集合 + 事件 ground truth + 邻居索引。"""

    def __init__(self, cfg: Optional[SyntheticCorpusConfig] = None):
        self.cfg = cfg or SyntheticCorpusConfig()
        self.points: List[InformationPoint] = []
        self.events: Dict[str, List[str]] = {}
        self._by_id: Dict[str, InformationPoint] = {}
        self._neighbors: Dict[str, List[Tuple[str, float]]] = {}
        self._event_start: Dict[str, float] = {}
        self._topic_vectors: List[Embedding] = []
        self._build()

    # ------------------------------------------------------------------
    # 生成
    # ------------------------------------------------------------------
    def _build(self) -> None:
        cfg = self.cfg
        rng = random.Random(cfg.seed)
        dim = cfg.embed_dim

        def _unit() -> Embedding:
            return normalize(tuple(rng.gauss(0.0, 1.0) for _ in range(dim)))

        self._topic_vectors = [_unit() for _ in range(cfg.n_topics)]
        source_weights = [
            cfg.source_min_weight + (1.0 - cfg.source_min_weight) * (i / max(cfg.source_count - 1, 1))
            for i in range(cfg.source_count)
        ]
        rng.shuffle(source_weights)  # 不按索引顺序给权重, 避免系统性偏差

        for e in range(cfg.n_events):
            event_id = f"evt{e:02d}"
            self.events[event_id] = []
            active = rng.sample(range(cfg.n_topics), cfg.topics_per_event)
            weights = [rng.random() for _ in active]
            wsum = sum(weights)
            weights = [w / wsum for w in weights]
            theme = normalize(
                tuple(
                    sum(weights[k] * self._topic_vectors[active[k]][d] for k in range(len(active)))
                    for d in range(dim)
                )
            )
            primary_source = rng.randrange(cfg.source_count)
            t_start = rng.uniform(0.0, cfg.time_horizon - cfg.event_span)
            self._event_start[event_id] = t_start

            for f in range(cfg.fragments_per_event):
                pid = f"{event_id}-f{f:02d}"
                noise = _unit()
                emb = normalize(tuple(theme[d] + cfg.within_event_noise * noise[d] for d in range(dim)))
                if rng.random() < cfg.primary_source_prob:
                    src = primary_source
                else:
                    src = rng.randrange(cfg.source_count)
                ts = t_start + rng.uniform(0.0, cfg.event_span)
                point = InformationPoint(
                    pid=pid,
                    event_id=event_id,
                    embedding=emb,
                    timestamp=ts,
                    source=f"s{src}",
                    source_weight=source_weights[src],
                    meta={"fragment_index": f, "event_index": e},
                )
                self.points.append(point)
                self._by_id[pid] = point
                self.events[event_id].append(pid)

        self._build_neighbor_index()

    def _build_neighbor_index(self) -> None:
        """预计算每点 top-m 语义最近邻(模拟离线构建的检索索引)。

        索引只按语义相似度构建; 时间/来源等结构信号在查询时打分,
        这样结构信号的作用可以被单独度量(诚实对比)。
        """
        cfg = self.cfg
        for p in self.points:
            scored = []
            for q in self.points:
                if q.pid == p.pid:
                    continue
                scored.append((cosine(p.embedding, q.embedding), q.pid))
            scored.sort(reverse=True)
            self._neighbors[p.pid] = [(pid, s) for s, pid in scored[: cfg.index_top_m]]

    # ------------------------------------------------------------------
    # 查询接口
    # ------------------------------------------------------------------
    def get(self, pid: str) -> InformationPoint:
        return self._by_id[pid]

    @property
    def point_ids(self) -> List[str]:
        return [p.pid for p in self.points]

    def event_of(self, pid: str) -> str:
        return self._by_id[pid].event_id

    def neighbors(self, pid: str, k: Optional[int] = None) -> List[Tuple[str, float]]:
        """索引查询: 返回 (邻居 pid, 余弦相似度), 已按相似度降序。"""
        lst = self._neighbors.get(pid, [])
        return lst[:k] if k is not None else lst

    def event_fragments(self, event_id: str) -> List[str]:
        return list(self.events.get(event_id, []))

    def observable_pids(self, t: float) -> List[str]:
        """时间 t 之前可观测的所有碎片(模拟信息未完整)。"""
        return [p.pid for p in self.points if p.timestamp <= t]

    def future_fragments(self, event_id: str, t: float) -> List[str]:
        """事件在时间 t 之后才出现的碎片(尚未观测)。"""
        return [pid for pid in self.events.get(event_id, []) if self.get(pid).timestamp > t]

    def embed_seed(self, seed_pids: Sequence[str]) -> Embedding:
        return mean_embedding([self.get(pid).embedding for pid in seed_pids])

    def sample_queries(
        self,
        n: int,
        rng_seed: int = 1,
        truncate_frac: Optional[float] = None,
    ) -> List[Query]:
        """采样查询: 每查询 = 一个种子碎片。

        truncate_frac: 若给定(0, 1), 查询时刻 = 事件开始 + frac × 事件跨度,
        只暴露该时刻前可观测的碎片(种子从可观测碎片中选取);
        否则全语料可见。
        """
        rng = random.Random(rng_seed)
        event_ids = sorted(self.events.keys())
        queries: List[Query] = []
        for i in range(n):
            event_id = rng.choice(event_ids)
            frags = self.events[event_id]
            t_obs = None
            if truncate_frac is not None:
                t_obs = self._event_start[event_id] + truncate_frac * self.cfg.event_span
                observable = [pid for pid in frags if self.get(pid).timestamp <= t_obs]
                if not observable:
                    observable = frags  # 极端情况兜底
                seed = rng.choice(observable)
                allowed = self.observable_pids(t_obs)
            else:
                seed = rng.choice(frags)
                allowed = None
            queries.append(
                Query(
                    qid=f"q{i:03d}",
                    seed_pids=[seed],
                    event_id=event_id,
                    allowed_pids=allowed,
                )
            )
        return queries

    # ------------------------------------------------------------------
    # 描述统计(用于实验文档与测试)
    # ------------------------------------------------------------------
    def similarity_stats(self, sample_size: int = 400) -> Dict[str, float]:
        """同事件/跨事件余弦相似度的抽样统计。"""
        rng = random.Random(self.cfg.seed + 999)
        within: List[float] = []
        cross: List[float] = []
        for _ in range(sample_size):
            ev = rng.choice(sorted(self.events.keys()))
            frags = self.events[ev]
            a, b = rng.sample(frags, 2)
            within.append(cosine(self.get(a).embedding, self.get(b).embedding))
        for _ in range(sample_size):
            ev1, ev2 = rng.sample(sorted(self.events.keys()), 2)
            a = rng.choice(self.events[ev1])
            b = rng.choice(self.events[ev2])
            cross.append(cosine(self.get(a).embedding, self.get(b).embedding))
        return {
            "within_mean": sum(within) / len(within),
            "cross_mean": sum(cross) / len(cross),
            "within_min": min(within),
            "cross_max": max(cross),
        }
