"""锚点检测: 多信号综合的 Anchor 选择。

Anchor 不是"最相似点", 而是综合以下信号的候选枢纽点:
- semantic similarity(与查询的语义接近度)
- source reliability(来源可靠性)
- temporal consistency(与种子时间接近度)
- local density(邻域密度/中心性)

**效率关键**: 候选池来自"种子沿索引的少量扩张", 而不是全库扫描
(否则锚点检测本身就 O(N), 摧毁 H-001 的效率主张)。
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence

from ..nets.search_net import NetSearchStats
from ..datasets.synthetic_events import SyntheticEventCorpus
from ..similarity import cosine
from ..types import Embedding


@dataclass
class AnchorConfig:
    n_anchors: int = 3
    pool_hops: int = 1  # 候选池扩张跳数(沿索引, 不扫全库; 1 跳即覆盖种子近邻)
    semantic_w: float = 1.0
    source_w: float = 0.5
    temporal_w: float = 0.3
    density_w: float = 0.4
    temporal_scale: float = 40.0  # 时间衰减尺度(与事件跨度同量级)


def detect_anchors(
    corpus: SyntheticEventCorpus,
    seed_pids: Sequence[str],
    query_emb: Optional[Embedding] = None,
    cfg: Optional[AnchorConfig] = None,
    stats: Optional[NetSearchStats] = None,
    allowed: Optional[Callable[[str], bool]] = None,
) -> List[str]:
    """返回按综合锚点分降序的前 n_anchors 个点(不含种子)。

    1. 候选池: 种子沿索引扩张 pool_hops 跳(只产生索引访问与局部评估);
    2. 锚点评分(池内点):
        anchor = (w_sem·sim + w_src·source + w_temp·temp + w_density·density) / Σw
        temp = exp(-|t_p - t_seed| / scale); density = |邻域| / max|邻域|。
    """
    cfg = cfg or AnchorConfig()
    stats = stats or NetSearchStats()
    query_emb = query_emb if query_emb is not None else corpus.embed_seed(seed_pids)

    seed_points = [corpus.get(pid) for pid in seed_pids]
    seed_time = sum(p.timestamp for p in seed_points) / max(len(seed_points), 1)
    max_density = max((len(corpus.neighbors(p.pid)) for p in corpus.points), default=1)
    wsum = cfg.semantic_w + cfg.source_w + cfg.temporal_w + cfg.density_w
    wsum = wsum if wsum > 0 else 1.0

    # 1) 候选池: 沿索引扩张
    pool: Dict[str, float] = {}
    frontier = list(seed_pids)
    for _ in range(max(1, cfg.pool_hops)):
        nxt: List[str] = []
        for pid in frontier:
            for nid, _sim in corpus.neighbors(pid):
                stats.index_lookups += 1
                if nid in seed_pids or nid in pool:
                    continue
                if allowed is not None and not allowed(nid):
                    continue
                pool[nid] = 0.0
                nxt.append(nid)
        frontier = nxt
        if not frontier:
            break

    # 2) 池内多信号锚点评分
    scored: List[tuple[float, str]] = []
    for pid in pool:
        p = corpus.get(pid)
        sem = cosine(query_emb, p.embedding)
        src = p.source_weight
        temp = math.exp(-abs(p.timestamp - seed_time) / cfg.temporal_scale)
        density = len(corpus.neighbors(pid)) / max_density
        combined = (
            cfg.semantic_w * sem
            + cfg.source_w * src
            + cfg.temporal_w * temp
            + cfg.density_w * density
        ) / wsum
        stats.similarity_calls += 1
        scored.append((combined, pid))

    scored.sort(reverse=True)
    return [pid for _, pid in scored[: cfg.n_anchors]]
