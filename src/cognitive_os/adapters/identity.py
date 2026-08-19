"""恒等适配器: 预计算向量 + 暴力邻居索引(行为等价基线)。

行为等价契约(E1 / ADR-0003): 本模块组合出的 CorpusView 与
SyntheticEventCorpus 对同一策略与查询产出逐字段一致的结果
(时延除外); 证明见 scripts/prove_protocol_equivalence.py 与
tests/test_protocol_equivalence.py。
"""

from __future__ import annotations

from collections.abc import Sequence

from ..protocols import Embedder, Index
from ..similarity import cosine, mean_embedding
from ..types import Embedding, InformationPoint


class IdentityEmbedder:
    """恒等嵌入: 直接取点上的预计算向量。"""

    def seed_vec(self, seed_points: Sequence[InformationPoint]) -> Embedding:
        return mean_embedding([p.embedding for p in seed_points])


class BruteForceIndex:
    """暴力邻居索引: 与 SyntheticEventCorpus 的邻居构建同算法、同序。"""

    def __init__(self, points: Sequence[InformationPoint], top_m: int):
        self._neighbors: dict[str, list[tuple[str, float]]] = {}
        for p in points:
            scored = []
            for q in points:
                if q.pid == p.pid:
                    continue
                scored.append((cosine(p.embedding, q.embedding), q.pid))
            scored.sort(reverse=True)
            self._neighbors[p.pid] = [(pid, s) for s, pid in scored[:top_m]]

    def neighbors(self, pid: str, k: int | None = None) -> list[tuple[str, float]]:
        lst = self._neighbors.get(pid, [])
        return lst[:k] if k is not None else lst


class CorpusView:
    """三协议组合体: 满足 Corpus 协议, 可直接喂给冻结策略。

    另附评估层便利成员(event_of / event_fragments / mentions);
    策略栈只依赖协议四成员。
    """

    def __init__(
        self,
        points: Sequence[InformationPoint],
        embedder: Embedder,
        index: Index,
    ):
        self.points = list(points)
        self.embedder = embedder
        self.index = index
        self._by_id = {p.pid: p for p in self.points}
        self._events: dict[str, list[str]] = {}
        for p in self.points:
            self._events.setdefault(p.event_id, []).append(p.pid)

    @property
    def point_ids(self) -> list[str]:
        return [p.pid for p in self.points]

    def get(self, pid: str) -> InformationPoint:
        return self._by_id[pid]

    def embed_seed(self, seed_pids: Sequence[str]) -> Embedding:
        return self.embedder.seed_vec([self.get(pid) for pid in seed_pids])

    def neighbors(self, pid: str, k: int | None = None) -> list[tuple[str, float]]:
        return self.index.neighbors(pid, k)

    def event_of(self, pid: str) -> str:
        return self._by_id[pid].event_id

    def event_fragments(self, event_id: str) -> list[str]:
        return list(self._events.get(event_id, []))

    def mentions(self, pid: str) -> list[str]:
        return list(self._by_id[pid].meta.get("mentions", []))


def identity_view(points, top_m: int) -> CorpusView:
    """从点集合构建恒等路径语料视图(纯标准库)。"""
    return CorpusView(
        points=points,
        embedder=IdentityEmbedder(),
        index=BruteForceIndex(points, top_m),
    )
