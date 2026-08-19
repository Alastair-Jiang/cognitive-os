"""EXP-004a Oracle Headroom: 异质性/上界测量(预注册运行器, R2)。

用法:
    python scripts/run_exp004a_oracle.py
    python scripts/run_exp004a_oracle.py --seeds 20260819,7,42,131,9999

预注册(冻结, 判定标准先于运行写下): research/experiments/EXP-004-adaptive-strategy-selection.md
- 语料宇宙: EXP-002 网格(OVERLAP×NOISE 全组合, 9 格, import 自 run_exp002_scan,
  不复制) + medium 档(configs/benchmark.medium.json 语料段, seed 逐轮覆盖),
  共 10 个独立参数配置。
  诚实备注: 预注册文本写「十格网格 + medium, 共 11 个」; BM-001 §7.1 与
  run_exp002_scan 的全组合为 3×3=9 格, +medium = 10 个不同参数配置
  (small 基准与 overlap-mid/noise-high 格参数全同, 不重复计)。
  G1 阈值按预注册原值执行: 池化 H1 至少 0.03 且至少 3 格格内 H1 至少 0.02
  (3/10 较文本中的 3/11 更严, 不放松任何阈值数值)。
- 语料 seed: 默认 {20260819, 7, 42}; 处于判定边界时按预注册扩展到 5 个
  (追加 {131, 9999})重跑并如实记录扩展(边界提示: 池化 H1 距 0.03 在
  0.005 内, 或 VERDICT 为 EDGE, 或达标格数恰在 2/3)。
- 查询: 每配置每 seed 12 个(query_seed=1), k=10, 无截断。
- 策略: A/B/C, 模板冻结(import SCAN_STRATEGY_TEMPLATE 与 build_strategies, D-5)。
- 效用: U_q(s) = F1@k 减去 lam·(sim_calls / N), N = 语料点数(EXP-001 口径:
  A 全扫约等于 N, sim/N 约 1.0); 主判定 lam=0.02; 敏感性 lam 取
  {0, 0.01, 0.02, 0.05, 0.1} 全部入汇总; 逐查询 F1/calls 落盘, 任意 lam 可复算。
- 定义: U_gf = 全局最优固定(全池); U_cf = 逐格最优固定; U_or = 逐查询事后最优;
  H0 = 各格 U_cf 均值减 U_gf(regime 级空间); H1 = 各格 (U_or 减 U_cf) 均值
  (查询级空间); 各格内查询数相同(36), 格均权 = 查询均权。
- G1(主 lam): PASS = 池化 H1 至少 0.03 且至少 3 格格内 H1 至少 0.02(进 004b);
  REGIME = H1 不达但池化 H0 至少 0.03(H-005 改写为 regime 级表述);
  FAIL = H0/H1 均不达(H-005 REFUTED, 当前语料宇宙无自适应空间);
  EDGE = 其余边界(如池化 H1 达标但达标格数不足, 预注册未命名的分支,
  如实标注, 不进 004b)。
判定只在 decide() 集中拼装(分层纪律); 统计口径参数入 meta(G4: 即便 G1 为
阈值闸门不用四闸门检验, meta 仍按预注册要求完整)。

诚实规则(宪法第 3 条): 所有数字以 JSON 为准; 判定失败如实报告。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_exp002_scan import (  # noqa: E402
    NOISE_LEVELS,
    N_TOPICS,
    OVERLAP_LEVELS,
    SCAN_STRATEGY_TEMPLATE,
    build_strategies,
    grid_corpus_config,
)

ROOT = Path(__file__).resolve().parents[1]

# ---- 预注册冻结参数(EXP-004 §设置 / §判定标准, 运行后不得回改) ----
SEEDS_DEFAULT = [20260819, 7, 42]
SEEDS_BOUNDARY_EXT = [131, 9999]
N_QUERIES = 12
QUERY_SEED = 1
K = 10
LAMBDA_MAIN = 0.02
LAMBDA_SWEEP = [0.0, 0.01, 0.02, 0.05, 0.1]
G1_H1_POOLED_MIN = 0.03
G1_H1_CELL_MIN = 0.02
G1_MIN_CELLS = 3
BOUNDARY_EPS = 0.005
EXPECTED_STRATEGIES = ("A-traditional", "B-anchor", "C-multinet")
CORPUS_UNIVERSE_NOTE = (
    "预注册文本写「十格网格 + medium, 共 11 个」; 实际独立参数配置 10 个: "
    "EXP-002 网格 3×3=9 格(BM-001 §7.1, run_exp002_scan.OVERLAP_LEVELS×"
    "NOISE_LEVELS) + medium 档(configs/benchmark.medium.json 语料段)。"
    "small 基准与 overlap-mid/noise-high 格参数全同, 不重复计。"
    "G1 阈值按预注册原值执行(至少 3 格; 3/10 较文本中的 3/11 更严)。"
)


def medium_corpus_params() -> dict[str, Any]:
    """medium 档语料参数(单一事实来源: configs/benchmark.medium.json, 去 seed)。"""
    cfg = json.loads(
        (ROOT / "configs" / "benchmark.medium.json").read_text(encoding="utf-8")
    )
    params = dict(cfg["corpus"])
    params.pop("seed", None)
    return params


def corpus_universe() -> list[dict[str, Any]]:
    """10 个独立语料配置: 9 网格格点(工厂零漂移) + medium 档。"""
    cells: list[dict[str, Any]] = []
    for ov_label, tpe in OVERLAP_LEVELS:
        for nz_label, noise in NOISE_LEVELS:
            cells.append(
                {
                    "cell": f"{ov_label}-{nz_label}",
                    "corpus_cfg": grid_corpus_config(tpe, noise, seed=0),
                    "params": {
                        "topics_per_event": tpe,
                        "within_event_noise": noise,
                        "n_topics": N_TOPICS,
                        "n_events": 12,
                        "fragments_per_event": 8,
                    },
                }
            )
    m = medium_corpus_params()
    cells.append(
        {
            "cell": "medium",
            "corpus_cfg": SyntheticCorpusConfig(**m, seed=0),
            "params": {
                k: m[k]
                for k in (
                    "n_events",
                    "fragments_per_event",
                    "n_topics",
                    "topics_per_event",
                    "within_event_noise",
                )
            },
        }
    )
    return cells


def utility(f1: float, sim_calls: float, n_points: int, lam: float) -> float:
    """U_q(s) = F1@k 减 lam·(sim_calls / N), N = 语料点数。"""
    return f1 - lam * sim_calls / n_points


def run_cell_seed(cell: dict[str, Any], corpus_seed: int, nq: int, k: int) -> dict[str, Any]:
    """单配置×单 seed: 建语料, 同查询集, 三策略逐查询记录(F1/calls/U)。"""
    cfg = replace(cell["corpus_cfg"], seed=corpus_seed)
    corpus = SyntheticEventCorpus(cfg)
    n_points = len(corpus.points)
    strategies = build_strategies(corpus, SCAN_STRATEGY_TEMPLATE)
    queries = corpus.sample_queries(nq, rng_seed=QUERY_SEED)
    per_query: dict[str, Any] = {}
    for q in queries:
        event_pids = set(corpus.event_fragments(q.event_id))
        relevant = {p for p in event_pids if q.is_allowed(p)} - set(q.seed_pids)
        rec: dict[str, Any] = {}
        for s in strategies:
            res = s.retrieve(q, k)
            p = precision_at_k(res.ranked_pids, relevant, k)
            r = recall_at_k(res.ranked_pids, relevant, k)
            f1 = f1_at_k(p, r)
            calls = float(res.similarity_calls)
            rec[s.name] = {
                "f1_at_k": f1,
                "similarity_calls": calls,
                "u_main": utility(f1, calls, n_points, LAMBDA_MAIN),
            }
        assert set(rec) == set(EXPECTED_STRATEGIES)
        per_query[q.qid] = {
            "event_id": q.event_id,
            "seed": q.seed_pids,
            "strategies": rec,
        }
    return {
        "corpus_seed": corpus_seed,
        "n_points": n_points,
        "per_query": per_query,
    }


def _per_query_us(runs: list, lam: float) -> list[dict[str, float]]:
    """把逐查询 F1/calls 折算成逐策略效用 U(任意 lam 可复算)。"""
    out: list[dict[str, float]] = []
    for run in runs:
        n = run["n_points"]
        for q in run["per_query"].values():
            rec = q["strategies"]
            out.append(
                {s: utility(rec[s]["f1_at_k"], rec[s]["similarity_calls"], n, lam) for s in EXPECTED_STRATEGIES}
            )
    return out


def aggregate_lambda(cells_runs: dict[str, Any], lam: float) -> dict[str, Any]:
    """按预注册定义计算 U_gf / U_cf / U_or / H0 / H1(逐格 + 池化)。"""
    cell_stats: dict[str, Any] = {}
    pool_u: dict[str, list] = {s: [] for s in EXPECTED_STRATEGIES}
    for cell, runs in cells_runs.items():
        us = _per_query_us(runs, lam)
        mean_u = {s: mean([u[s] for u in us]) for s in EXPECTED_STRATEGIES}
        best = max(EXPECTED_STRATEGIES, key=lambda s: mean_u[s])
        u_cf = mean_u[best]
        u_or = mean([max(u.values()) for u in us])
        cell_stats[cell] = {
            "mean_u": mean_u,
            "u_cf": u_cf,
            "best_fixed": best,
            "u_or": u_or,
        }
        for s in EXPECTED_STRATEGIES:
            pool_u[s].extend(u[s] for u in us)
    pool_mean = {s: mean(v) for s, v in pool_u.items()}
    gf_key = max(EXPECTED_STRATEGIES, key=lambda s: pool_mean[s])
    u_gf = pool_mean[gf_key]
    for c in cell_stats.values():
        c["h0"] = c["u_cf"] - u_gf
        c["h1"] = c["u_or"] - c["u_cf"]
    h0_pooled = mean([c["h0"] for c in cell_stats.values()])
    h1_pooled = mean([c["h1"] for c in cell_stats.values()])
    return {
        "lambda": lam,
        "u_gf": u_gf,
        "u_gf_strategy": gf_key,
        "pooled_mean_u": pool_mean,
        "cells": cell_stats,
        "h0_pooled": h0_pooled,
        "h1_pooled": h1_pooled,
    }


def per_seed_pooled_h1(cells_runs: dict[str, Any], lam: float) -> dict[str, float]:
    """逐 seed 池化 H1(描述性一致性证据, 非 G1 闸门)。"""
    seeds = sorted({r["corpus_seed"] for runs in cells_runs.values() for r in runs})
    out: dict[str, float] = {}
    for sd in seeds:
        h1s: list[float] = []
        for cell, runs in cells_runs.items():
            rs = [r for r in runs if r["corpus_seed"] == sd]
            us = _per_query_us(rs, lam)
            if not us:
                continue
            mean_u = {s: mean([u[s] for u in us]) for s in EXPECTED_STRATEGIES}
            u_cf = max(mean_u.values())
            u_or = mean([max(u.values()) for u in us])
            h1s.append(u_or - u_cf)
        out[str(sd)] = mean(h1s) if h1s else 0.0
    return out


def decide(agg_main: dict[str, Any]) -> dict[str, Any]:
    """G1 判定(预注册, 只在此拼装; 三态 + 未命名边界如实标注)。"""
    h1 = agg_main["h1_pooled"]
    h0 = agg_main["h0_pooled"]
    n_ok = sum(1 for c in agg_main["cells"].values() if c["h1"] >= G1_H1_CELL_MIN)
    gates = {
        "g1a_pooled_h1_ge_0.03": h1 >= G1_H1_POOLED_MIN,
        "g1b_cells_h1_ge_0.02_ge_3": n_ok >= G1_MIN_CELLS,
        "g1r_pooled_h0_ge_0.03": h0 >= G1_H1_POOLED_MIN,
    }
    if gates["g1a_pooled_h1_ge_0.03"] and gates["g1b_cells_h1_ge_0.02_ge_3"]:
        verdict = "PASS"
    elif (not gates["g1a_pooled_h1_ge_0.03"]) and gates["g1r_pooled_h0_ge_0.03"]:
        verdict = "REGIME"
    elif (not gates["g1a_pooled_h1_ge_0.03"]) and (not gates["g1r_pooled_h0_ge_0.03"]):
        verdict = "FAIL"
    else:
        verdict = "EDGE"
    boundary = (
        abs(h1 - G1_H1_POOLED_MIN) <= BOUNDARY_EPS
        or verdict == "EDGE"
        or n_ok in (G1_MIN_CELLS - 1, G1_MIN_CELLS)
    )
    note = ""
    if boundary:
        note = (
            "结果处于判定边界: 按预注册条款可扩展语料 seed 到 5 个"
            f"(追加 {SEEDS_BOUNDARY_EXT})重跑并如实记录扩展"
        )
    return {
        "verdict": verdict,
        "pooled_h1": h1,
        "pooled_h0": h0,
        "cells_with_h1_ge_0.02": n_ok,
        "n_cells": len(agg_main["cells"]),
        "gates": gates,
        "boundary_flag": boundary,
        "boundary_note": note,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-004a Oracle Headroom(预注册)")
    ap.add_argument("--seeds", default=",".join(str(s) for s in SEEDS_DEFAULT))
    ap.add_argument("--queries", type=int, default=N_QUERIES)
    ap.add_argument("--k", type=int, default=K)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    if not seeds:
        ap.error("--seeds 至少一个")

    universe = corpus_universe()
    cells_runs: dict[str, Any] = {}
    for cell in universe:
        runs = []
        for sd in seeds:
            print(f"[EXP-004a] {cell['cell']} seed={sd} …", flush=True)
            runs.append(run_cell_seed(cell, sd, args.queries, args.k))
        cells_runs[cell["cell"]] = runs

    agg_by_lambda: dict[str, Any] = {}
    for lam in LAMBDA_SWEEP:
        agg_by_lambda[str(lam)] = aggregate_lambda(cells_runs, lam)
    judgment = decide(agg_by_lambda[str(LAMBDA_MAIN)])
    per_seed = per_seed_pooled_h1(cells_runs, LAMBDA_MAIN)

    ts = time.strftime("%Y%m%d-%H%M%S")
    default_out = ROOT / "research" / "results"
    out = Path(args.out) if args.out else default_out
    out.mkdir(parents=True, exist_ok=True)
    out_path = out / f"EXP-004a-oracle-s{len(seeds)}-q{args.queries}-{ts}.json"
    payload = {
        "meta": {
            "schema_version": "EXP-004a/1",
            "experiment": "EXP-004a",
            "prereg": "research/experiments/EXP-004-adaptive-strategy-selection.md(冻结)",
            "seeds": seeds,
            "k": args.k,
            "n_queries_per_cell_seed": args.queries,
            "query_seed": QUERY_SEED,
            "lambda_main": LAMBDA_MAIN,
            "lambda_sweep": LAMBDA_SWEEP,
            "stats_params": {
                "n_resample": 10000,
                "alpha": 0.05,
                "perm_seed": 777,
                "boot_seed": 888,
            },
            "strategy_template": "run_exp002_scan.SCAN_STRATEGY_TEMPLATE(冻结 import, D-5)",
            "corpus_universe_note": CORPUS_UNIVERSE_NOTE,
            "g1_thresholds": {
                "h1_pooled_min": G1_H1_POOLED_MIN,
                "h1_cell_min": G1_H1_CELL_MIN,
                "min_cells": G1_MIN_CELLS,
            },
            "timestamp": ts,
        },
        "cells_params": {c["cell"]: c["params"] for c in universe},
        "cells_runs": cells_runs,
        "aggregate_by_lambda": agg_by_lambda,
        "per_seed_pooled_h1_main_lambda": per_seed,
        "judgment": judgment,
    }
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    main_agg = agg_by_lambda[str(LAMBDA_MAIN)]
    print(
        f"\n=== EXP-004a Oracle Headroom (lambda={LAMBDA_MAIN}, "
        f"{len(seeds)} seeds x {len(universe)} cells) ==="
    )
    print(
        f"U_gf={main_agg['u_gf']:.4f} ({main_agg['u_gf_strategy']})  "
        f"H0_pooled={main_agg['h0_pooled']:+.4f}  "
        f"H1_pooled={main_agg['h1_pooled']:+.4f}"
    )
    hdr = ["cell", "best_fixed", "U_cf", "U_or", "H0", "H1", "H1ge0.02"]
    print("  ".join(f"{h:>14}" for h in hdr))
    for cname in main_agg["cells"]:
        c = main_agg["cells"][cname]
        row = [
            cname,
            c["best_fixed"],
            f"{c['u_cf']:.4f}",
            f"{c['u_or']:.4f}",
            f"{c['h0']:+.4f}",
            f"{c['h1']:+.4f}",
            "Y" if c["h1"] >= G1_H1_CELL_MIN else "-",
        ]
        print("  ".join(f"{v:>14}" for v in row))
    print(
        f"\nG1 verdict: {judgment['verdict']}  "
        f"(cells_with_h1_ge_0.02 = "
        f"{judgment['cells_with_h1_ge_0.02']}/{judgment['n_cells']})"
    )
    for kk, v in judgment["gates"].items():
        print(f"  {kk}: {'PASS' if v else 'FAIL'}")
    if judgment["boundary_flag"]:
        print(f"  边界提示: {judgment['boundary_note']}")
    print(f"\n原始数据: {out_path}")


if __name__ == "__main__":
    main()
