"""统计推断模块测试(黄金值 + 确定性 + 边界)。"""

import sys
import unittest
from math import isclose, isfinite
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.stats import (  # noqa: E402
    bootstrap_mean_ci,
    mean_dz,
    paired_diffs,
    permutation_test,
)


class TestPairedDiffs(unittest.TestCase):
    def test_basic(self):
        diffs = paired_diffs([0.5, 0.9], [0.4, 0.6])
        self.assertAlmostEqual(diffs[0], 0.1)
        self.assertAlmostEqual(diffs[1], 0.3)

    def test_integer_inputs_exact(self):
        self.assertEqual(paired_diffs([3, 5], [1, 2]), [2.0, 3.0])

    def test_length_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            paired_diffs([0.1], [0.1, 0.2])


class TestMeanDz(unittest.TestCase):
    def test_zero_var_zero_mean(self):
        self.assertEqual(mean_dz([0.0, 0.0]), 0.0)

    def test_zero_var_positive(self):
        self.assertEqual(mean_dz([0.08, 0.08, 0.08]), float("inf"))

    def test_hand_computable(self):
        # d = [1, 3]: mean=2, var=1, d_z=2
        self.assertTrue(isclose(mean_dz([1.0, 3.0]), 2.0))

    def test_tiny_rejected(self):
        with self.assertRaises(ValueError):
            mean_dz([1.0])


class TestPermutationTest(unittest.TestCase):
    def test_strong_positive_p_floor(self):
        # 全部同号: |mean| 已达零分布上限。
        # 但 sign-flip 随机化检验的 p 下限为 2/2^n(n=10 时差值全部同号
        # 的翻号组合只有 2 种:全正/全负, 占 2^10=1024 种里的 2/1024≈0.002),
        # 而非 1/(1+R)——这是小样本配对随机化检验的固有分辨率。
        diffs = [0.08] * 10
        res = permutation_test(diffs, n_resample=10000, rng_seed=777)
        self.assertLess(res["p_value"], 0.01)
        self.assertAlmostEqual(res["obs_mean_diff"], 0.08)

    def test_symmetric_around_zero_near_p1(self):
        # 完全对称: T=0, 每个 |T'|>=0, p = (1+10000)/(1+10000) = 1.0
        diffs = [0.05, -0.05, 0.05, -0.05, 0.05, -0.05]
        res = permutation_test(diffs, n_resample=10000, rng_seed=777)
        self.assertEqual(res["p_value"], 1.0)

    def test_seed_determinism(self):
        diffs = [0.03, -0.01, 0.07, 0.02, -0.004, 0.05]
        r1 = permutation_test(diffs, n_resample=2000, rng_seed=42)
        r2 = permutation_test(diffs, n_resample=2000, rng_seed=42)
        self.assertEqual(r1, r2)

    def test_low_resample_rejected(self):
        with self.assertRaises(ValueError):
            permutation_test([0.1, 0.2], n_resample=10)

    def test_tiny_rejected(self):
        with self.assertRaises(ValueError):
            permutation_test([0.5])


class TestBootstrapMeanCI(unittest.TestCase):
    def test_ci_brackets_mean(self):
        values = [0.05, 0.07, 0.03, 0.08, -0.01, 0.04, 0.06, 0.02]
        res = bootstrap_mean_ci(values, n_resample=5000, rng_seed=888)
        self.assertLessEqual(res["ci_low"], res["mean"])
        self.assertLessEqual(res["mean"], res["ci_high"])

    def test_hand_bounds(self):
        # 常量样本: CI 退化为该值
        res = bootstrap_mean_ci([0.42] * 8, n_resample=1000, rng_seed=888)
        self.assertEqual(res["ci_low"], res["mean"])
        self.assertEqual(res["ci_high"], res["mean"])
        self.assertTrue(isclose(res["mean"], 0.42))

    def test_seed_determinism(self):
        values = [0.03, -0.01, 0.07, 0.02, -0.004, 0.05]
        r1 = bootstrap_mean_ci(values, n_resample=2000, rng_seed=5)
        r2 = bootstrap_mean_ci(values, n_resample=2000, rng_seed=5)
        self.assertEqual(r1, r2)

    def test_alpha_validation(self):
        with self.assertRaises(ValueError):
            bootstrap_mean_ci([0.1, 0.2], alpha=1.5)
        with self.assertRaises(ValueError):
            bootstrap_mean_ci([0.1, 0.2], alpha=0.0)

    def test_ci_width_shrinks_with_n(self):
        small = bootstrap_mean_ci([0.05, 0.07], n_resample=5000, rng_seed=888)
        large = bootstrap_mean_ci(
            [0.05, 0.07] * 50, n_resample=5000, rng_seed=888
        )
        w_small = small["ci_high"] - small["ci_low"]
        w_large = large["ci_high"] - large["ci_low"]
        self.assertLess(w_large, w_small)
        self.assertTrue(isfinite(w_large) and isfinite(w_small))


if __name__ == "__main__":
    unittest.main()
