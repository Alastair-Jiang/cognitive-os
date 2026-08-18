"""锚点检测测试。"""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.anchors.anchor_detector import AnchorConfig, detect_anchors
from cognitive_os.datasets.synthetic_events import SyntheticEventCorpus
from cognitive_os.nets.search_net import NetSearchStats
from cognitive_os.similarity import cosine


def _pool_pids(corpus, seed_pids, hops):
    """复刻检测器候选池(测试用)。"""
    pool = set()
    frontier = list(seed_pids)
    for _ in range(hops):
        nxt = []
        for pid in frontier:
            for nid, _ in corpus.neighbors(pid):
                if nid not in seed_pids and nid not in pool:
                    pool.add(nid)
                    nxt.append(nid)
        frontier = nxt
    return pool


class TestAnchorDetection(unittest.TestCase):
    def setUp(self):
        self.corpus = SyntheticEventCorpus()
        self.query = self.corpus.sample_queries(1, rng_seed=11)[0]
        self.q_emb = self.corpus.embed_seed(self.query.seed_pids)

    def test_anchors_distinct_and_not_seeds(self):
        cfg = AnchorConfig(n_anchors=3)
        anchors = detect_anchors(self.corpus, self.query.seed_pids, self.q_emb, cfg=cfg)
        self.assertEqual(len(anchors), 3)
        self.assertEqual(len(set(anchors)), 3)
        self.assertTrue(all(a not in self.query.seed_pids for a in anchors))

    def test_semantic_focused_anchor_is_most_similar(self):
        """semantic_w=1 时, 锚点 = 池内与查询最相似的点。"""
        cfg = AnchorConfig(n_anchors=1, semantic_w=1.0, source_w=0.0, temporal_w=0.0, density_w=0.0)
        anchors = detect_anchors(self.corpus, self.query.seed_pids, self.q_emb, cfg=cfg)
        pool = _pool_pids(self.corpus, self.query.seed_pids, cfg.pool_hops)
        expected = max(pool, key=lambda pid: cosine(self.q_emb, self.corpus.get(pid).embedding))
        self.assertEqual(anchors[0], expected)

    def test_source_focused_anchors_reliabler_than_semantic(self):
        """来源导向的锚点, 平均来源可靠性高于语义导向的锚点(多查询聚合)。"""
        src_cfg = AnchorConfig(
            n_anchors=4, semantic_w=0.0, source_w=1.0, temporal_w=0.0, density_w=0.0
        )
        sem_cfg = AnchorConfig(
            n_anchors=4, semantic_w=1.0, source_w=0.0, temporal_w=0.0, density_w=0.0
        )
        src_total, sem_total, n = 0.0, 0.0, 0
        for query in self.corpus.sample_queries(5, rng_seed=21):
            q_emb = self.corpus.embed_seed(query.seed_pids)
            src_anchors = detect_anchors(self.corpus, query.seed_pids, q_emb, cfg=src_cfg)
            sem_anchors = detect_anchors(self.corpus, query.seed_pids, q_emb, cfg=sem_cfg)
            src_total += (
                sum(self.corpus.get(a).source_weight for a in src_anchors) / len(src_anchors)
            )
            sem_total += (
                sum(self.corpus.get(a).source_weight for a in sem_anchors) / len(sem_anchors)
            )
            n += 1
        self.assertGreater(src_total / n, sem_total / n)

    def test_anchor_detection_cost_is_local(self):
        """候选池机制: 锚点检测的相似度计算数必须 << 全库点数(效率主张)。"""
        stats = NetSearchStats()
        detect_anchors(self.corpus, self.query.seed_pids, self.q_emb, stats=stats)
        self.assertLess(stats.similarity_calls, len(self.corpus.points))


if __name__ == "__main__":
    unittest.main()
