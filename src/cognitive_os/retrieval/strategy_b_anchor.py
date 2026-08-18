"""Strategy B: Anchor-based Retrieval(锚点导向检索)。

流程(H-001 / RQ-2):
1. 找少量高置信 Anchor(多信号综合: 语义+来源+时间+局部密度);
2. 围绕 Anchor(与种子)沿索引局部扩张;
3. 按组合证据分排序。

设计动机: 相比全库两两比较 O(N²), 锚点+扩张只评估锚点邻域内的点,
期望在不显著损失 Recall 的情况下降低 similarity_calls。
"""

from __future__ import annotations

import time
from typing import List, Optional

from ..anchors.anchor_detector import AnchorConfig, detect_anchors
from ..nets.search_net import NetSearchStats, SearchNet, SearchNetConfig
from ..types import Query, RetrievalResult
from .base import RetrievalStrategy


class AnchorRetrieval(RetrievalStrategy):
    name = "B-anchor"

    def __init__(
        self,
        corpus,
        anchor_cfg: Optional[AnchorConfig] = None,
        net_cfg: Optional[SearchNetConfig] = None,
    ):
        super().__init__(corpus)
        self.anchor_cfg = anchor_cfg or AnchorConfig()
        self.net_cfg = net_cfg or SearchNetConfig(name="B-expansion")

    def retrieve(self, query: Query, k: int) -> RetrievalResult:
        t0 = time.perf_counter()
        stats = NetSearchStats()
        q_emb = self.corpus.embed_seed(query.seed_pids)
        allowed = query.is_allowed

        anchors: List[str] = detect_anchors(
            self.corpus,
            query.seed_pids,
            q_emb,
            cfg=self.anchor_cfg,
            stats=stats,
            allowed=allowed,
        )

        net = SearchNet(self.corpus, self.net_cfg)
        candidates = net.search(
            query.seed_pids,
            q_emb,
            extra_frontier=anchors,
            stats=stats,
            allowed=allowed,
        )

        ranked = [e.pid for e in candidates[:k]]
        scores = [e.score for e in candidates[:k]]
        evidence = {e.pid: e for e in candidates}
        latency_ms = (time.perf_counter() - t0) * 1000.0
        iterations = 1 + max(1, self.net_cfg.max_hops)  # 锚点检测 1 轮 + 扩张跳数
        return RetrievalResult(
            qid=query.qid,
            strategy=self.name,
            ranked_pids=ranked,
            scores=scores,
            evidence=evidence,
            iterations=iterations,
            similarity_calls=stats.similarity_calls,
            index_lookups=stats.index_lookups,
            latency_ms=latency_ms,
            notes={"anchors": anchors},
        )
