"""三种检索策略测试。"""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.anchors.anchor_detector import AnchorConfig
from cognitive_os.datasets.synthetic_events import SyntheticEventCorpus
from cognitive_os.nets.search_net import SearchNetConfig
from cognitive_os.retrieval.strategy_a_traditional import TraditionalRetrieval
from cognitive_os.retrieval.strategy_b_anchor import AnchorRetrieval
from cognitive_os.retrieval.strategy_c_multinet import DynamicMultiNetRetrieval
from cognitive_os.validation.progressive import ValidatorConfig


def _make_c():
    return DynamicMultiNetRetrieval(
        SyntheticEventCorpus(),
        net_configs=[
            SearchNetConfig(name="n1", radius=0.88, semantic_w=1.0, max_hops=1),
            SearchNetConfig(name="n2", radius=0.7, semantic_w=0.5, source_w=0.4, temporal_window=40.0),
        ],
        validator_cfg=ValidatorConfig(),
    )


class TestStrategyA(unittest.TestCase):
    def setUp(self):
        self.corpus = SyntheticEventCorpus()
        self.query = self.corpus.sample_queries(1, rng_seed=2)[0]
        self.strat = TraditionalRetrieval(self.corpus, source_bonus=0.05)

    def test_returns_k_distinct(self):
        res = self.strat.retrieve(self.query, k=10)
        self.assertEqual(len(res.ranked_pids), 10)
        self.assertEqual(len(set(res.ranked_pids)), 10)
        self.assertTrue(all(pid not in self.query.seed_pids for pid in res.ranked_pids))

    def test_flat_scan_cost_is_n(self):
        res = self.strat.retrieve(self.query, k=10)
        # 全库扫描, 但种子自身不参与检索
        self.assertEqual(res.similarity_calls, len(self.corpus.points) - len(self.query.seed_pids))

    def test_recall_reasonable(self):
        res = self.strat.retrieve(self.query, k=10)
        relevant = set(self.corpus.event_fragments(self.query.event_id)) - set(self.query.seed_pids)
        hits = sum(1 for pid in res.ranked_pids if pid in relevant)
        self.assertGreater(hits, 0)

    def test_truncation_respects_allowed(self):
        q = self.corpus.sample_queries(1, rng_seed=2, truncate_frac=0.5)[0]
        res = self.strat.retrieve(q, k=10)
        self.assertTrue(all(q.is_allowed(pid) for pid in res.ranked_pids))


class TestStrategyB(unittest.TestCase):
    def setUp(self):
        self.corpus = SyntheticEventCorpus()
        self.query = self.corpus.sample_queries(1, rng_seed=2)[0]
        self.strat = AnchorRetrieval(
            self.corpus,
            anchor_cfg=AnchorConfig(n_anchors=3),
            net_cfg=SearchNetConfig(name="B", radius=0.72, temporal_window=40.0, max_hops=1),
        )
        self.strat_a = TraditionalRetrieval(self.corpus, source_bonus=0.05)

    def test_returns_distinct_candidates_with_anchors(self):
        """B 返回去重候选(≤ k 个, 锚点+扩张的覆盖), 并记录锚点。"""
        res = self.strat.retrieve(self.query, k=10)
        self.assertLessEqual(len(res.ranked_pids), 10)
        self.assertGreaterEqual(len(res.ranked_pids), 1)
        self.assertEqual(len(set(res.ranked_pids)), len(res.ranked_pids))
        self.assertGreater(len(res.notes.get("anchors", [])), 0)

    def test_cheaper_than_flat_scan(self):
        """H-001 核心断言: 锚点+扩张的相似度计算数显著少于全库扫描。"""
        res_a = self.strat_a.retrieve(self.query, k=10)
        res_b = self.strat.retrieve(self.query, k=10)
        self.assertLess(res_b.similarity_calls, res_a.similarity_calls)
        self.assertLess(res_b.similarity_calls, 0.5 * res_a.similarity_calls)

    def test_recall_not_catastrophic(self):
        """B 的 Recall 相对 A 的损失不应是灾难性的(具体判定交给 BM-001/H-001)。"""
        res_a = self.strat_a.retrieve(self.query, k=10)
        res_b = self.strat.retrieve(self.query, k=10)
        relevant = set(self.corpus.event_fragments(self.query.event_id)) - set(self.query.seed_pids)
        from cognitive_os.metrics import recall_at_k

        ra = recall_at_k(res_a.ranked_pids, relevant, 10)
        rb = recall_at_k(res_b.ranked_pids, relevant, 10)
        self.assertLessEqual(ra - rb, 0.5)


class TestStrategyC(unittest.TestCase):
    def setUp(self):
        self.corpus = SyntheticEventCorpus()
        self.query = self.corpus.sample_queries(1, rng_seed=2)[0]
        self.strat = _make_c()

    def test_returns_k_distinct(self):
        res = self.strat.retrieve(self.query, k=10)
        self.assertEqual(len(res.ranked_pids), 10)
        self.assertEqual(len(set(res.ranked_pids)), 10)

    def test_budget_bounded(self):
        res = self.strat.retrieve(self.query, k=10)
        self.assertLessEqual(res.iterations, self.strat.validator_cfg.max_rounds)

    def test_no_hard_drop(self):
        """多轮后候选未被删光(至少 k 个且证据表非空)。"""
        res = self.strat.retrieve(self.query, k=10)
        self.assertGreaterEqual(len(res.evidence), 10)

    def test_scores_are_confidences(self):
        res = self.strat.retrieve(self.query, k=10)
        for pid, score in zip(res.ranked_pids, res.scores):
            self.assertAlmostEqual(res.evidence[pid].confidence, score)

    def test_truncation_respects_allowed(self):
        q = self.corpus.sample_queries(1, rng_seed=2, truncate_frac=0.5)[0]
        res = self.strat.retrieve(q, k=10)
        self.assertTrue(all(q.is_allowed(pid) for pid in res.ranked_pids))


class TestStrategiesConsistentInterface(unittest.TestCase):
    def test_all_strategies_return_same_interface(self):
        corpus = SyntheticEventCorpus()
        query = corpus.sample_queries(1, rng_seed=9)[0]
        strategies = [
            TraditionalRetrieval(corpus, source_bonus=0.05),
            AnchorRetrieval(corpus),
            _make_c(),
        ]
        for s in strategies:
            res = s.retrieve(query, k=10)
            self.assertEqual(res.qid, query.qid)
            self.assertEqual(res.strategy, s.name)
            self.assertGreaterEqual(res.latency_ms, 0.0)
            self.assertGreaterEqual(res.similarity_calls, 0)
            self.assertGreaterEqual(res.iterations, 1)


if __name__ == "__main__":
    unittest.main()
