"""统计推断(显著性检验与区间估计), 纯标准库。

对应工程化路线图 E0(实验与评测平台基线)的判定层:
- TREC/IR 社区惯例: per-query 配对度量差 + 重抽样检验, 不做正态性假设;
- 双侧配对随机化检验(sign-flip permutation test):
  Smucker, Allan, Carterette (2007, CIKM) 推荐的随机化检验标准形;
- bootstrap 百分位区间: 同一配对样本上的均值区间;
- 全部固定 rng_seed, 完全可复现(宪法第 1 条: 可复现才算证据)。

设计约束:
- 零依赖(与测量工具 metrics.py 同级: 度量 vs 推断, 分工不混);
- 无 p-hacking 手段: 检验类型、重采样次数、alpha 全部在配置外露,
  默认双侧; 不支持"便宜就换个口径"的一键分支;
- 样本量门槛: 差值样本不足 2 时抛错而不是返回假精确值。
"""

from __future__ import annotations

import math
import random
from collections.abc import Sequence


def paired_diffs(a: Sequence[float], b: Sequence[float]) -> list[float]:
    """配对差向量 d_i = a_i - b_i(两序列同序一一配对)。"""
    if len(a) != len(b):
        raise ValueError(f"配对序列长度必须一致, 收到 {len(a)} vs {len(b)}")
    return [x - y for x, y in zip(a, b)]


def mean_dz(diffs: Sequence[float]) -> float:
    """配对差的标准化效应量(Cohen's d_z = mean(d) / SD(d), SD 用总体口径)。

    SD=0(所有差相同)时: mean=0 -> 0.0; 否则按 mean 符号返回 ±inf
    (同号常数差意味着无限大的标准化效应, 如实记录)。
    """
    if len(diffs) < 2:
        raise ValueError(f"效应量需要至少 2 个配对差, 收到 {len(diffs)}")
    n = len(diffs)
    m = sum(diffs) / n
    var = sum((d - m) ** 2 for d in diffs) / n
    if var == 0.0:
        if m == 0.0:
            return 0.0
        return math.inf if m > 0 else -math.inf
    return m / math.sqrt(var)


def permutation_test(
    diffs: Sequence[float],
    n_resample: int = 10000,
    rng_seed: int = 777,
) -> dict[str, float]:
    """双侧配对随机化检验(sign-flip permutation test)。

    设 per-query 差向量 d = (d_1, ..., d_n), H0: d_i 关于 0 对称
    (两策略 per-query 度量无系统差异)。

    检验统计量 T = mean(d)。零分布构造: 对每个 d_i 独立随机乘 ±1
    得到 d', 计算 T' = mean(d')。双侧 p 值:
        p = (1 + #{|T'| >= |T|}) / (1 + n_resample)
    含自身一次(避免 p=0, IR 社区惯例)。
    """
    if len(diffs) < 2:
        raise ValueError(f"随机化检验需要至少 2 个配对差, 收到 {len(diffs)}")
    if n_resample < 1000:
        raise ValueError(f"n_resample 过小({n_resample}), 至少 1000")
    rng = random.Random(rng_seed)
    n = len(diffs)
    t_obs = sum(diffs) / n
    obs_abs = abs(t_obs)
    extreme = 0
    for _ in range(n_resample):
        t = 0.0
        for d in diffs:
            t += d if rng.randrange(2) == 0 else -d
        t /= n
        if abs(t) >= obs_abs - 1e-12:  # 浮点容差, 不完全严格的边界计入
            extreme += 1
    return {
        "obs_mean_diff": t_obs,
        "p_value": (1 + extreme) / (1 + n_resample),
        "n": float(n),
        "n_resample": float(n_resample),
    }


def bootstrap_mean_ci(
    values: Sequence[float],
    n_resample: int = 10000,
    alpha: float = 0.05,
    rng_seed: int = 888,
) -> dict[str, float]:
    """bootstrap 百分位均值区间(对输入样本有放回重采样)。

    对配对差 values 重采样 B = n_resample 次, 每次记 mean;
    区间取均值分布的 [alpha/2, 1-alpha/2] 分位点。
    返回总体均值的样本区间——CI 不含 0 ⇔ 双侧 alpha 水平有方向性。
    """
    if len(values) < 2:
        raise ValueError(f"区间估计需要至少 2 个样本, 收到 {len(values)}")
    if n_resample < 1000:
        raise ValueError(f"n_resample 过小({n_resample}), 至少 1000")
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha 必须在 (0,1), 收到 {alpha}")
    rng = random.Random(rng_seed)
    n = len(values)
    means: list[float] = []
    for _ in range(n_resample):
        s = 0.0
        for _ in range(n):
            s += values[rng.randrange(n)]
        means.append(s / n)
    means.sort()
    lo_i = max(0, min(n_resample - 1, int(alpha / 2 * n_resample)))
    hi_i = max(0, min(n_resample - 1, int((1.0 - alpha / 2) * n_resample)))
    return {
        "mean": sum(values) / n,
        "ci_low": means[lo_i],
        "ci_high": means[hi_i],
        "alpha": alpha,
        "n": float(n),
        "n_resample": float(n_resample),
    }
