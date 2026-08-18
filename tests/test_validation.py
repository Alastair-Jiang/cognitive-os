"""渐进式验证器测试。"""

import sys
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.types import Evidence
from cognitive_os.validation.progressive import ProgressiveValidator, ValidatorConfig


class TestProgressiveValidator(unittest.TestCase):
    def test_no_hard_pruning(self):
        """低置信度候选不被删除, 只是降权(宪法: 防止提前淘汰)。"""
        v = ProgressiveValidator()
        v.mark_round()
        v.add_round([Evidence(pid="p", score=0.9), Evidence(pid="q", score=0.1)])
        v.mark_round()
        v.add_round([Evidence(pid="p", score=0.9)])
        v.update_confidence()
        self.assertIn("p", v.evidence)
        self.assertIn("q", v.evidence)  # q 仍在证据表中
        self.assertGreater(v.evidence["p"].confidence, v.evidence["q"].confidence)

    def test_consensus_widens_gap(self):
        """跨网共识: 被更多网支持的候选, 与单网候选的置信度差距扩大。"""
        v = ProgressiveValidator(ValidatorConfig(consensus_w=0.4))
        v.mark_round()
        v.add_round([Evidence(pid="p", score=0.8), Evidence(pid="q", score=0.6)])
        v.update_confidence()
        gap1 = v.evidence["p"].confidence - v.evidence["q"].confidence
        v.mark_round()
        v.add_round([Evidence(pid="p", score=0.8)])  # 只有 p 得到二次支持
        v.update_confidence()
        gap2 = v.evidence["p"].confidence - v.evidence["q"].confidence
        self.assertGreater(gap2, gap1)

    def test_stabilization_early_stop(self):
        v = ProgressiveValidator(
            ValidatorConfig(
                confidence_threshold=1.5,  # 永不达阈值
                stabilization_eps=1e-6,
                stabilize_rounds=2,
                max_rounds=10,
            )
        )
        stopped = False
        for _ in range(10):
            v.mark_round()
            v.add_round([Evidence(pid="p", score=0.8), Evidence(pid="q", score=0.7)])
            v.update_confidence()
            if v.should_stop(2):
                stopped = True
                break
        self.assertTrue(stopped)
        self.assertEqual(v.stopped_reason, "stabilized")
        self.assertLessEqual(v.rounds_run, 4)

    def test_budget_limit(self):
        """预算用尽必须停止(max_rounds); 分数逐轮变化防止误触稳定早停。"""
        v = ProgressiveValidator(
            ValidatorConfig(
                confidence_threshold=1.5,
                stabilization_eps=0.0,  # 只有完全不变才算稳定
                stabilize_rounds=2,
                max_rounds=3,
            )
        )
        for score in (0.5, 0.6, 0.7):
            v.mark_round()
            v.add_round([Evidence(pid="p", score=score)])
            v.update_confidence()
            if v.should_stop(2):
                break
        self.assertEqual(v.rounds_run, 3)
        self.assertEqual(v.stopped_reason, "budget")

    def test_final_ranked_keeps_all(self):
        """最终排序保留全部候选; 共识(跨网支持)可让低分高共识候选胜出。"""
        v = ProgressiveValidator(ValidatorConfig(consensus_w=0.4))
        v.mark_round()
        v.add_round([Evidence(pid="a", score=0.9), Evidence(pid="b", score=0.5)])
        v.mark_round()
        v.add_round([Evidence(pid="b", score=0.6), Evidence(pid="c", score=0.4)])
        ranked = v.final_ranked(2)
        self.assertEqual(len(ranked), 2)
        # b: 0.6*0.6 + 0.4*1.0(两轮共识) = 0.76 > a: 0.6*0.9 + 0.4*0.5 = 0.74
        self.assertEqual(ranked[0], "b")
        self.assertEqual(set(v.evidence.keys()), {"a", "b", "c"})


if __name__ == "__main__":
    unittest.main()
