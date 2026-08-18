"""合成事件语料测试。"""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.datasets.synthetic_events import SyntheticCorpusConfig, SyntheticEventCorpus
from cognitive_os.similarity import cosine


class TestSyntheticCorpus(unittest.TestCase):
    def test_deterministic_reproducible(self):
        c1 = SyntheticEventCorpus(SyntheticCorpusConfig(seed=42))
        c2 = SyntheticEventCorpus(SyntheticCorpusConfig(seed=42))
        self.assertEqual(len(c1.points), len(c2.points))
        for p1, p2 in zip(c1.points, c2.points):
            self.assertEqual(p1.embedding, p2.embedding)
            self.assertEqual(p1.timestamp, p2.timestamp)
            self.assertEqual(p1.source_weight, p2.source_weight)

    def test_event_sizes_and_unique_pids(self):
        cfg = SyntheticCorpusConfig()
        corpus = SyntheticEventCorpus(cfg)
        self.assertEqual(len(corpus.events), cfg.n_events)
        pids = [p.pid for p in corpus.points]
        self.assertEqual(len(pids), len(set(pids)))
        for event_id, frags in corpus.events.items():
            self.assertEqual(len(frags), cfg.fragments_per_event)
            for pid in frags:
                self.assertEqual(corpus.event_of(pid), event_id)

    def test_within_similarity_above_cross(self):
        """同事件碎片平均相似度必须显著高于跨事件(合成数据的基本结构)。"""
        corpus = SyntheticEventCorpus()
        s = corpus.similarity_stats()
        self.assertGreater(s["within_mean"], 0.7)
        self.assertGreater(s["within_mean"] - s["cross_mean"], 0.15)

    def test_ambiguity_present(self):
        """跨事件必须存在非平凡相似对(对应'苹果问题'的歧义)。"""
        corpus = SyntheticEventCorpus()
        s = corpus.similarity_stats()
        self.assertGreater(s["cross_max"], 0.4)

    def test_neighbor_index(self):
        corpus = SyntheticEventCorpus()
        for p in corpus.points:
            neigh = corpus.neighbors(p.pid)
            self.assertLessEqual(len(neigh), corpus.cfg.index_top_m)
            self.assertTrue(all(nid != p.pid for nid, _ in neigh))
            sims = [s for _, s in neigh]
            self.assertEqual(sims, sorted(sims, reverse=True))
            # 第一个邻居必须是相似度最高者(浮点比较取 12 位精度)
            if neigh:
                top = max(
                    (cosine(p.embedding, corpus.get(q.pid).embedding), q.pid)
                    for q in corpus.points
                    if q.pid != p.pid
                )
                self.assertEqual(neigh[0][0], top[1])
                self.assertAlmostEqual(neigh[0][1], top[0], places=12)

    def test_sample_queries_full(self):
        corpus = SyntheticEventCorpus()
        queries = corpus.sample_queries(5, rng_seed=3)
        self.assertEqual(len(queries), 5)
        for q in queries:
            self.assertEqual(len(q.seed_pids), 1)
            self.assertEqual(corpus.event_of(q.seed_pids[0]), q.event_id)
            self.assertIsNone(q.allowed_pids)

    def test_sample_queries_truncation(self):
        """截断模式下: 种子可观测, allowed 集合只含时间 <= t_obs 的碎片。"""
        corpus = SyntheticEventCorpus()
        queries = corpus.sample_queries(8, rng_seed=5, truncate_frac=0.5)
        for q in queries:
            seed = q.seed_pids[0]
            self.assertTrue(q.is_allowed(seed))
            self.assertIsNotNone(q.allowed_pids)
            t_obs = max(corpus.get(pid).timestamp for pid in q.allowed_pids)
            for pid in q.allowed_pids:
                self.assertLessEqual(corpus.get(pid).timestamp, t_obs)


if __name__ == "__main__":
    unittest.main()
