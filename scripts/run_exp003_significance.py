"""EXP-003 多种子显著性复核: OV-MD/NZ-MD 格点 C vs A 的差异是否真实。

背景(诚实规则, 宪法第 3 条):
- EXP-002 扫描在 topics_per_event=4, within_event_noise=0.30 单 seed 下
  观察到 C F1 > A F1(+0.137); 单 seed 单 k 无统计支撑, 仅算"附带观察"。
- 本脚本对同一格点跑多种子: 每个语料 seed 下 A/C 同查询集的 per-query
  F1 配对差; 判定用 ci/stats.py(随机化检验 + bootstrap 区间 + 效应量)。
- 判定标准(预注册, 见 research/experiments/EXP-003):
  同时满足 → SUPPORTED; 任一不满足 → INCONCLUSIVE:
    (1) 配对随机化检验 p < 0.05(双侧);
    (2) bootstrap 95% 均值差区间不含 0;
    (3) 方向一致: 每 seed mean_diff ≥ 0 的占比 ≥ 80%(要求跨 seed 可重
        现, 而非个别语料偶然);
    (4) |mean_diff| ≥ 0.01(排除统计显著物理无意义的尘埃效应);
  若 (1)(2) 显著但 |mean_diff| ≤ -0.01 → REFUTED(方向反转, 如实记录)。

用法:
    python scripts/run_exp003_significance.py [--seeds 20260819,7,42] [--queries 12]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.datasets.synthetic_events import (  # noqa: E402
    SyntheticCorpusConfig,
    SyntheticEventCorpus,
)
from cognitive_os.metrics import (  # noqa: E402
    f1_at_k,
    mean,
    precision_at_k,
    recall_at_k,
)
from cognitive_os.stats import (  # noqa: E402
    bootstrap_mean_ci,
    mean_dz,
    paired_diffs,
    permutation_test,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_exp002_scan import SCAN_STRATEGY_TEMPLATE, build_strategies  # noqa: E402

# 复核格点(与 run_exp002_scan.py 同名档位完全一致, 不得漂移)
CELL_TOPICS_PER_EVENT = 4      # "overlap-mid"
CELL_WITHIN_EVENT_NOISE = 0.30  # "noise-mid"
STRATEGIES_UNDERCLAIM = ["A-traditional", "C-multinet"]  # 只主张 C vs A


def run_seed(corpus_seed: int, nq: int, k: int) -> Dict[str, Any]:
    """单 seed: 建语料 → 同查询集 → A/C 配对 per-query F1。"""
    corpus = SyntheticEventCorpus(
        SyntheticCorpusConfig(
            n_events=12,
            fragments_per_event=8,
            embed_dim=24,
            n_topics=5,
            topics_per_event=CELL_TOPICS_PER_EVENT,
            within_event_noise=CELL_WITHIN_EVENT_NOISE,
            time_horizon=100.0,
            event_span=20.0,
            source_count=4,
            source_min_weight=0.6,
            primary_source_prob=0.6,
            index_top_m=6,
            seed=corpus_seed,
        )
    )
    queries = corpus.sample_queries(nq, rng_seed=1)
    strategies = {s.name: s for s in build_strategies(corpus, SCAN_STRATEGY_TEMPLATE)}
    a, c = strategies["A-traditional"], strategies["C-multinet"]

    a_f1: List[float] = []
    c_f1: List[float] = []
    a_calls: List[float] = []
    c_calls: List[float] = []
    for q in queries:
        event_pids = set(corpus.event_fragments(q.event_id))
        relevant = {p for p in event_pids if q.is_allowed(p)} - set(q.seed_pids)

        res_a = a.retrieve(q, k)
        pa = precision_at_k(res_a.ranked_pids, relevant, k)
        ra = recall_at_k(res_a.ranked_pids, relevant, k)
        a_f1.append(f1_at_k(pa, ra))
        a_calls.append(float(res_a.similarity_calls))

        res_c = c.retrieve(q, k)
        pc = precision_at_k(res_c.ranked_pids, relevant, k)
        rc = recall_at_k(res_c.ranked_pids, relevant, k)
        c_f1.append(f1_at_k(pc, rc))
        c_calls.append(float(res_c.similarity_calls))

    diffs = paired_diffs(c_f1, a_f1)  # C - A
    return {
        "corpus_seed": corpus_seed,
        "n_queries": nq,
        "A_f1_mean": mean(a_f1),
        "C_f1_mean": mean(c_f1),
        "mean_diff": mean(diffs),
        "A_sim_calls_mean": mean(a_calls),
        "C_sim_calls_mean": mean(c_calls),
        "diffs": diffs,
    }


def decide(
    all_diffs: List[float],
    per_seed_mean_diffs: List[float],
) -> Dict[str, Any]:
    """预注册判定(见 EXP-003 文档 §判定标准)。"""
    p_res = permutation_test(all_diffs, n_resample=10000, rng_seed=777)
    ci_res = bootstrap_mean_ci(all_diffs, n_resample=10000, alpha=0.05, rng_seed=888)
    dz = mean_dz(all_diffs)
    pos_seeds = sum(1 for m in per_seed_mean_diffs if m >= 0.0)
    consistency = pos_seeds / len(per_seed_mean_diffs)
    obs = p_res["obs_mean_diff"]

    q1 = p_res["p_value"] < 0.05
    q2 = not (ci_res["ci_low"] <= 0.0 <= ci_res["ci_high"])
    q3 = consistency >= 0.8
    q4 = abs(obs) >= 0.01

    if q1 and q2 and q3 and q4:
        verdict = "SUPPORTED"
    if q1 and q2 and q4 and obs <= -0.01:
        verdict = "REFUTED"
    if not (q1 and q2 and q3 and q4) and not (q1 and q2 and q4 and obs <= -0.01):
        verdict = "INCONCLUSIVE"

    return {
        "verdict": verdict,
        "obs_mean_diff": obs,
        "p_value": p_res["p_value"],
        "ci_low": ci_res["ci_low"],
        "ci_high": ci_res["ci_high"],
        "mean_dz": dz,
        "pos_seeds_ratio": consistency,
        "gates": {
            "q1_p_lt_0.05": q1,
            "q2_ci_excludes_0": q2,
            "q3_seed_consistency_>=80%": q3,
            "q4_min_effect_>=1pp": q4,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-003 多种子显著性复核")
    ap.add_argument("--seeds", default="20260819,7,42,131,9999",
                        help="语料 seed 列表, 默认 5 个(预注册)")
    ap.add_argument("--queries", type=int, default=12)
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]

    rows: List[Dict[str, Any]] = []
    for s in seeds:
        print(f"[EXP-003] corpus_seed={s} ({seeds.index(s)+1}/{len(seeds)}) …", flush=True)
        rows.append(run_seed(s, args.queries, args.k))

    all_diffs: List[float] = [d for r in rows for d in r["diffs"]]
    per_seed_mean_diffs = [r["mean_diff"] for r in rows]
    judgement = decide(all_diffs, per_seed_mean_diffs)

    ts = time.strftime("%Y%m%d-%H%M%S")
    default_out = Path(__file__).resolve().parents[1] / "research" / "results"
    out = Path(args.out) if args.out else default_out
    out.mkdir(parents=True, exist_ok=True)
    out_path = out / f"EXP-003-significance-s{len(seeds)}-q{args.queries}-{ts}.json"
    payload = {
        "meta": {
            "experiment": "EXP-003",
            "cell": "overlap-mid(tpe=4)/noise-mid(0.30)",
            "seeds": seeds,
            "n_queries_per_seed": args.queries,
            "k": args.k,
            "strategy_template": "run_exp002_scan.SCAN_STRATEGY_TEMPLATE(冻结)",
            "stats_params": {
                "n_resample": 10000,
                "alpha": 0.05,
                "perm_seed": 777,
                "boot_seed": 888,
            },
            "timestamp": ts,
        },
        "per_seed": [
            {key: v for key, v in r.items() if key != "diffs"} for r in rows
        ],
        "all_diffs": all_diffs,
        "judgement": judgement,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== EXP-003 overlap-mid/noise-mid C vs A ===")
    header = f"{'seed':>12} " + " ".join(
        f"{h:>10}" for h in ["A F1", "C F1", "diff", "A calls", "C calls"]
    )
    print(header)
    for r in rows:
        line = (
            f"{r['corpus_seed']:>12} {r['A_f1_mean']:>10.3f} "
            f"{r['C_f1_mean']:>10.3f} {r['mean_diff']:>10.3f} "
            f"{r['A_sim_calls_mean']:>10.0f} {r['C_sim_calls_mean']:>10.0f}"
        )
        print(line)
    g = judgement["gates"]
    print(f"\nverdict: {judgement['verdict']}")
    print(f"  mean_diff={judgement['obs_mean_diff']:+.3f} "
          f"p={judgement['p_value']:.4f} "
          f"CI=[{judgement['ci_low']:+.3f},{judgement['ci_high']:+.3f}] "
          f"dz={judgement['mean_dz']:+.2f} "
          f"seed+={judgement['pos_seeds_ratio']:.0%}")
    for kk, v in g.items():
        print(f"  {kk}: {'PASS' if v else 'FAIL'}")
    print(f"\n原始数据: {out_path}")


if __name__ == "__main__":
    main()
