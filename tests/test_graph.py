"""证据图测试。"""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.datasets.synthetic_events import SyntheticEventCorpus
from cognitive_os.graph.evidence_graph import EvidenceGraph
from cognitive_os.types import InformationPoint


class _StubCorpus:
    """仅用于构造图的迷你语料桩(避免依赖完整生成器)。"""

    def __init__(self, points):
        self._by_id = {p.pid: p for p in points}

    def get(self, pid):
        return self._by_id[pid]


class TestEvidenceGraph(unittest.TestCase):
    def setUp(self):
        self.corpus = SyntheticEventCorpus()

    def test_isolated_component(self):
        """低于语义阈值的两点不成边, 成分各自孤立。"""
        a = InformationPoint(
            pid="a", event_id="e1", embedding=(1.0, 0.0, 0.0),
            timestamp=0.0, source="s1", source_weight=0.9,
        )
        b = InformationPoint(
            pid="b", event_id="e2", embedding=(0.0, 1.0, 0.0),
            timestamp=1.0, source="s1", source_weight=0.9,
        )
        stub = _StubCorpus([a, b])
        g = EvidenceGraph.build(stub, ["a", "b"], semantic_threshold=0.8)
        self.assertEqual(g.component_of("a"), ["a"])
        self.assertEqual(g.component_of("b"), ["b"])

    def test_temporal_window_blocks_edge(self):
        """语义相似但时间相距过远的点对不成边。"""
        a = InformationPoint(
            pid="a", event_id="e1", embedding=(1.0, 0.0),
            timestamp=0.0, source="s1", source_weight=0.9,
        )
        b = InformationPoint(
            pid="b", event_id="e1", embedding=(0.99, 0.1),
            timestamp=90.0, source="s1", source_weight=0.9,
        )
        stub = _StubCorpus([a, b])
        g = EvidenceGraph.build(stub, ["a", "b"], semantic_threshold=0.8, temporal_window=5.0)
        self.assertFalse(g.has_edge("a", "b"))
        g2 = EvidenceGraph.build(stub, ["a", "b"], semantic_threshold=0.8, temporal_window=None)
        self.assertTrue(g2.has_edge("a", "b"))

    def test_source_diversity_requirement(self):
        """require_source_diversity=True 时, 同来源点对不成边。"""
        a = InformationPoint(
            pid="a", event_id="e1", embedding=(1.0, 0.0),
            timestamp=0.0, source="s1", source_weight=0.9,
        )
        b = InformationPoint(
            pid="b", event_id="e1", embedding=(0.99, 0.1),
            timestamp=1.0, source="s1", source_weight=0.9,
        )
        c = InformationPoint(
            pid="c", event_id="e1", embedding=(0.98, 0.2),
            timestamp=2.0, source="s2", source_weight=0.8,
        )
        stub = _StubCorpus([a, b, c])
        g = EvidenceGraph.build(
            stub, ["a", "b", "c"], semantic_threshold=0.8, require_source_diversity=True
        )
        self.assertFalse(g.has_edge("a", "b"))
        self.assertTrue(g.has_edge("a", "c"))

    def test_component_purity_and_reconstruction(self):
        """同事件碎片在多信号图中连通(高歧义语料下用 0.72 阈值)。"""
        corpus = self.corpus
        event_id = sorted(corpus.events.keys())[0]
        frags = corpus.event_fragments(event_id)
        foreign = next(pid for pid in corpus.point_ids if corpus.event_of(pid) != event_id)
        candidates = frags + [foreign]
        g = EvidenceGraph.build(corpus, candidates, semantic_threshold=0.72, temporal_window=30.0)
        comp = g.component_of(frags[0])
        # 成分包含种子 + 至少一个同事件碎片(连通性成立)
        self.assertGreaterEqual(len(set(comp) & set(frags)), 2)
        purity = EvidenceGraph.cluster_purity(comp, {p: corpus.event_of(p) for p in comp})
        self.assertGreaterEqual(purity, 0.5)
        recon = EvidenceGraph.reconstruction(comp, set(frags))
        self.assertGreater(recon["f1"], 0.0)

    def test_components_partition(self):
        corpus = self.corpus
        g = EvidenceGraph.build(
            corpus, corpus.point_ids, semantic_threshold=0.85, temporal_window=30.0
        )
        comps = g.components()
        seen = set()
        for comp in comps:
            self.assertFalse(seen & set(comp))
            seen.update(comp)


if __name__ == "__main__":
    unittest.main()
