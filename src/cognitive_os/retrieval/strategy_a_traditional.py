"""Strategy A: 传统扁平 top-k 检索(基线)。

对全语料逐一计算与查询的相似度, 取 top-k。
这是检索质量的参考基线, 也是计算成本的参考基线
(一次查询 = N 次相似度计算, 无索引、无渐进验证)。
"""

from __future__ import annotations

import time

from ..similarity import cosine
from ..types import Evidence, Query, RetrievalResult
from .base import RetrievalStrategy


class TraditionalRetrieval(RetrievalStrategy):
    name = "A-traditional"

    def __init__(self, corpus, source_bonus: float = 0.05):
        super().__init__(corpus)
        self.source_bonus = source_bonus

    def retrieve(self, query: Query, k: int) -> RetrievalResult:
        t0 = time.perf_counter()
        q_emb = self.corpus.embed_seed(query.seed_pids)
        scored = []
        evidence: dict[str, Evidence] = {}
        sim_calls = 0
        for pid in self.corpus.point_ids:
            if pid in query.seed_pids:
                continue  # 种子不可检索
            if not query.is_allowed(pid):
                continue
            p = self.corpus.get(pid)
            sem = cosine(q_emb, p.embedding)
            s = sem + self.source_bonus * p.source_weight
            sim_calls += 1
            scored.append((s, pid))
            evidence[pid] = Evidence(
                pid=pid,
                score=s,
                semantic_sim=sem,
                source_evidence=p.source_weight,
                confidence=s,
            )
        scored.sort(reverse=True)
        ranked = [pid for _, pid in scored[:k]]
        scores = [s for s, _ in scored[:k]]
        latency_ms = (time.perf_counter() - t0) * 1000.0
        return RetrievalResult(
            qid=query.qid,
            strategy=self.name,
            ranked_pids=ranked,
            scores=scores,
            evidence=evidence,
            iterations=1,
            similarity_calls=sim_calls,
            index_lookups=0,
            latency_ms=latency_ms,
            notes={"source_bonus": self.source_bonus},
        )
