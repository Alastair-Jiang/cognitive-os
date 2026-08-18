"""检索网(Search Net): 一个可配置的搜索策略原语。

"网"不是物理网络, 而是一种 Dynamic Search / Retrieval Strategy。
每个网可配置: 相似度半径、时间窗、来源最小权重、扩张跳数、
各信号的权重(semantic / source / temporal / structural)。
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass

from ..datasets.synthetic_events import SyntheticEventCorpus
from ..similarity import cosine
from ..types import Embedding, Evidence


@dataclass
class SearchNetConfig:
    name: str = "net"
    radius: float = 0.80  # 邻居相似度下限(过滤弱邻居)
    temporal_window: float | None = None  # 时间窗; None = 忽略时间信号
    source_min_weight: float = 0.0  # 低于该可靠性的来源不进入候选
    max_candidates_per_anchor: int = 5  # 每轮扩张预算(按锚点数放大)
    max_hops: int = 2
    semantic_w: float = 1.0
    source_w: float = 0.0
    temporal_w: float = 0.0
    structural_w: float = 0.0  # 邻域支持度(作为结构一致性的廉价代理)


@dataclass
class NetSearchStats:
    """一次搜索的效率计数(诚实计量, 宪法第 3 条)。"""

    similarity_calls: int = 0  # 相似度评估次数(计算/API 成本代理)
    index_lookups: int = 0  # 索引访问次数
    candidates_scored: int = 0


class SearchNet:
    """围绕种子(与可选锚点)扩张的单网搜索。"""

    def __init__(self, corpus: SyntheticEventCorpus, cfg: SearchNetConfig | None = None):
        self.corpus = corpus
        self.cfg = cfg or SearchNetConfig()
        self.name = self.cfg.name

    def _combined(
        self,
        sem: float,
        src: float,
        temp: float,
        struct: float,
    ) -> float:
        c = self.cfg
        wsum = c.semantic_w + c.source_w + c.temporal_w + c.structural_w
        if wsum <= 0.0:
            return 0.0
        return (
            c.semantic_w * sem
            + c.source_w * src
            + c.temporal_w * temp
            + c.structural_w * struct
        ) / wsum

    def search(
        self,
        seed_pids: Sequence[str],
        query_emb: Embedding | None = None,
        extra_frontier: Sequence[str] = (),
        stats: NetSearchStats | None = None,
        allowed: Callable[[str], bool] | None = None,
    ) -> list[Evidence]:
        """从种子(与额外前沿点, 如锚点)出发, 沿索引做多跳扩张。

        返回按组合证据分降序的候选 Evidence 列表(不含种子本身)。
        """
        stats = stats or NetSearchStats()
        c = self.cfg
        corpus = self.corpus
        query_emb = query_emb if query_emb is not None else corpus.embed_seed(seed_pids)
        seed_points = [corpus.get(pid) for pid in seed_pids]
        seed_time = sum(p.timestamp for p in seed_points) / max(len(seed_points), 1)

        visited = set(seed_pids) | set(extra_frontier)
        candidates: dict[str, Evidence] = {}
        frontier = list(seed_pids) + list(extra_frontier)

        for _ in range(max(1, c.max_hops)):
            next_frontier: list[tuple[float, str]] = []
            for pid in frontier:
                for nid, nsim in corpus.neighbors(pid):
                    stats.index_lookups += 1
                    if nid in visited:
                        continue
                    if allowed is not None and not allowed(nid):
                        continue  # 未观测碎片视为不存在(信息未完整场景)
                    point = corpus.get(nid)
                    if nsim < c.radius:
                        continue
                    if point.source_weight < c.source_min_weight:
                        continue
                    sem = cosine(query_emb, point.embedding)
                    src = point.source_weight
                    if c.temporal_window is not None:
                        temp = math.exp(-abs(point.timestamp - seed_time) / c.temporal_window)
                    else:
                        temp = 0.0
                    struct = 1.0  # 处于前沿点邻域内 = 结构支持(廉价代理)
                    combined = self._combined(sem, src, temp, struct)
                    stats.similarity_calls += 1
                    stats.candidates_scored += 1
                    ev = candidates.get(nid)
                    if ev is None or combined > ev.score:
                        candidates[nid] = Evidence(
                            pid=nid,
                            score=combined,
                            semantic_sim=sem,
                            source_evidence=src,
                            temporal_evidence=temp,
                            structural_evidence=struct,
                        )
                    next_frontier.append((combined, nid))
            if not next_frontier:
                break
            next_frontier.sort(reverse=True)
            budget = max(1, c.max_candidates_per_anchor * max(len(frontier), 1))
            frontier = [nid for _, nid in next_frontier[:budget]]

        ranked = sorted(candidates.values(), key=lambda e: e.score, reverse=True)
        return ranked
