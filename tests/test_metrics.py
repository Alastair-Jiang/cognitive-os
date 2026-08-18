"""指标函数测试。"""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.metrics import (
    cluster_purity,
    f1_at_k,
    mrr,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reconstruction_metrics,
)


class TestRankMetrics(unittest.TestCase):
    def setUp(self):
        self.ranked = ["a", "b", "c", "d", "e"]
        self.relevant = {"c", "e"}

    def test_precision_recall(self):
        self.assertAlmostEqual(precision_at_k(self.ranked, self.relevant, 3), 1 / 3)
        self.assertAlmostEqual(recall_at_k(self.ranked, self.relevant, 3), 0.5)
        self.assertAlmostEqual(f1_at_k(1 / 3, 0.5), 0.4)

    def test_ndcg(self):
        # rewards = [0,0,1] ; dcg = 1/log2(4)=0.5; idcg = 1 + 1/log2(3)
        import math

        idcg3 = 1.0 + 1.0 / math.log2(3)
        self.assertAlmostEqual(ndcg_at_k(self.ranked, self.relevant, 3), 0.5 / idcg3)
        # 全部相关排在前面 → ndcg = 1
        self.assertAlmostEqual(ndcg_at_k(["c", "e", "a"], self.relevant, 3), 1.0)

    def test_mrr(self):
        self.assertAlmostEqual(mrr(self.ranked, self.relevant), 1 / 3)
        self.assertEqual(mrr(["x", "y"], self.relevant), 0.0)

    def test_empty_guards(self):
        self.assertEqual(precision_at_k([], self.relevant, 5), 0.0)
        self.assertEqual(recall_at_k(["a"], set(), 5), 0.0)
        self.assertEqual(ndcg_at_k(["a"], set(), 5), 0.0)


class TestReconstructionMetrics(unittest.TestCase):
    def test_cluster_purity(self):
        pid_to_event = {"a": "e1", "b": "e1", "c": "e2"}
        self.assertAlmostEqual(cluster_purity(["a", "b", "c"], pid_to_event), 2 / 3)
        self.assertAlmostEqual(cluster_purity(["a", "b"], pid_to_event), 1.0)
        self.assertEqual(cluster_purity([], pid_to_event), 0.0)

    def test_reconstruction(self):
        m = reconstruction_metrics(["a", "b", "c"], {"a", "b", "d"})
        self.assertAlmostEqual(m["precision"], 2 / 3)
        self.assertAlmostEqual(m["recall"], 2 / 3)
        self.assertAlmostEqual(m["f1"], 2 / 3)


if __name__ == "__main__":
    unittest.main()
