"""证据图(Evidence Graph): 多信号一致性建图。

对应 H-003 / RQ-4: 判断"这些点共同组成某个有效信息结构"时,
不能只依赖语义相似度(local similarity ≠ global same event)。
图中边要求**多信号一致**:
- 语义相似度 ≥ 阈值;
- 时间一致性(时间窗内);
- 可选: 来源多样性(不同来源互相印证, 而不是同一来源复述)。
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Set, Tuple

from ..similarity import cosine
from ..datasets.synthetic_events import SyntheticEventCorpus


class EvidenceGraph:
    """候选点上的无向一致性图。"""

    def __init__(self) -> None:
        self.edges: Dict[Tuple[str, str], float] = {}  # (a, b) -> weight, a < b
        self.adj: Dict[str, Set[str]] = {}

    def add_edge(self, a: str, b: str, weight: float) -> None:
        key = (a, b) if a < b else (b, a)
        if key in self.edges:
            return
        self.edges[key] = weight
        self.adj.setdefault(a, set()).add(b)
        self.adj.setdefault(b, set()).add(a)

    def has_edge(self, a: str, b: str) -> bool:
        return (a, b) in self.edges or (b, a) in self.edges

    @classmethod
    def build(
        cls,
        corpus: SyntheticEventCorpus,
        candidate_pids: Iterable[str],
        semantic_threshold: float = 0.7,
        temporal_window: Optional[float] = None,
        require_source_diversity: bool = False,
        max_edges_per_node: Optional[int] = None,
        causal_edges: bool = False,
    ) -> "EvidenceGraph":
        """在候选点之间按多信号一致性建边。

        causal_edges: 启用时, 显式提及/引用关系(meta["mentions"])也建边——
        引用是硬结构信号, 不依赖语义阈值(跨事件因果/传播链)。

        max_edges_per_node: 单点最大度数上限(防止稠密图);
        None = 不限制(第一版小语料不限制)。
        """
        g = cls()
        candidates = list(candidate_pids)
        deg: Dict[str, int] = {}

        # 引用边: 先建(硬结构边), 与语义边独立
        if causal_edges:
            pid_set = set(candidates)
            for a in candidates:
                for b in corpus.mentions(a):
                    if b not in pid_set:
                        continue
                    if max_edges_per_node is not None and (
                        deg.get(a, 0) >= max_edges_per_node or deg.get(b, 0) >= max_edges_per_node
                    ):
                        continue
                    g.add_edge(a, b, 1.0)  # 引用 = 确定性结构信号, 权重 1.0
                    deg[a] = deg.get(a, 0) + 1
                    deg[b] = deg.get(b, 0) + 1

        for i, a in enumerate(candidates):
            pa = corpus.get(a)
            for b in candidates[i + 1 :]:
                pb = corpus.get(b)
                if max_edges_per_node is not None and (
                    deg.get(a, 0) >= max_edges_per_node or deg.get(b, 0) >= max_edges_per_node
                ):
                    continue
                sim = cosine(pa.embedding, pb.embedding)
                if sim < semantic_threshold:
                    continue
                if temporal_window is not None and abs(pa.timestamp - pb.timestamp) > temporal_window:
                    continue
                if require_source_diversity and pa.source == pb.source:
                    continue
                weight = sim * (0.5 + 0.5 * min(pa.source_weight, pb.source_weight))
                g.add_edge(a, b, weight)
                deg[a] = deg.get(a, 0) + 1
                deg[b] = deg.get(b, 0) + 1
        return g

    def component_of(self, pid: str) -> List[str]:
        """pid 所在的连通成分(BFS)。孤立点返回 [pid]。"""
        if pid not in self.adj:
            return [pid]
        seen = {pid}
        stack = [pid]
        while stack:
            cur = stack.pop()
            for nxt in self.adj.get(cur, ()):
                if nxt not in seen:
                    seen.add(nxt)
                    stack.append(nxt)
        return sorted(seen)

    def components(self) -> List[List[str]]:
        seen: Set[str] = set()
        comps: List[List[str]] = []
        for pid in self.adj:
            if pid in seen:
                continue
            comp = self.component_of(pid)
            seen.update(comp)
            comps.append(comp)
        return comps

    @staticmethod
    def cluster_purity(component_pids: List[str], pid_to_event: Dict[str, str]) -> float:
        """连通成分的纯度: 最大事件占比(1.0 = 单一事件)。"""
        from ..metrics import cluster_purity as _purity

        return _purity(component_pids, pid_to_event)

    @staticmethod
    def reconstruction(component_pids: List[str], true_event_pids: Set[str]) -> Dict[str, float]:
        from ..metrics import reconstruction_metrics

        return reconstruction_metrics(component_pids, true_event_pids)
