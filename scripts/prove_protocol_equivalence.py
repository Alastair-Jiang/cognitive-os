"""E1 行为等价证明(ADR-0001 / ADR-0003 验收条件)。

恒等适配器路径(CorpusView + IdentityEmbedder + BruteForceIndex)与
直接路径(SyntheticEventCorpus)对同一配置、同一查询集、同一冻结策略
产出逐字段一致的结果; 并与既有 EXP-001 冻结结果 JSON 的聚合指标对账
(时延除外, 聚合在 1e-12 容差内一致)。

用法:
    python scripts/prove_protocol_equivalence.py
    python scripts/prove_protocol_equivalence.py --queries 30 --truncate 0.6

输出: research/results/PROOF-E1-EQUIV-*.json(回执, 只追加)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "src"
for _p in (str(HERE), str(SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from cognitive_os.adapters.identity import identity_view  # noqa: E402
from cognitive_os.datasets.synthetic_events import (  # noqa: E402
    SyntheticCorpusConfig,
    SyntheticEventCorpus,
)
from cognitive_os.metrics import mean  # noqa: E402

import run_benchmark  # noqa: E402  (D-5: 复用构建与单查询逻辑, 不复制)

COMPARE_KEYS = [
    "ranked_pids",
    "scores",
    "similarity_calls",
    "index_lookups",
    "iterations",
    "early_stopped",
]
METRIC_KEYS = ("precision_at_k", "recall_at_k", "f1_at_k", "ndcg_at_k", "mrr")
GRAPH_KEYS = ("purity", "recon_f1", "purity_semantic_only")


def run_path(corpus, s_cfg, queries, k, g_cfg, truncate_frac):
    """一条路径(直接或视图)的全部查询结果与策略名。"""
    strategies = run_benchmark.build_strategies(corpus, s_cfg)
    per_q = {}
    for q in queries:
        event_pids = set(corpus.event_fragments(q.event_id))
        relevant = {p for p in event_pids if q.is_allowed(p)} - set(q.seed_pids)
        future = (
            {p for p in event_pids if not q.is_allowed(p)}
            if truncate_frac is not None
            else set()
        )
        per_q[q.qid] = {
            s.name: run_benchmark.run_one(
                corpus, s, q, k, g_cfg, truncate_frac, relevant, future
            )
            for s in strategies
        }
    return per_q, [s.name for s in strategies]


def path_diffs(direct, via_view) -> list[str]:
    """逐字段差异(空列表 = 完全一致; 时延不在比较范围)。"""
    out = []
    for qid, by_s in direct.items():
        for s_name, r1 in by_s.items():
            r2 = via_view[qid][s_name]
            for key in COMPARE_KEYS:
                if r1[key] != r2[key]:
                    out.append(f"{qid} {s_name} {key}: 直接={r1[key]} 视图={r2[key]}")
            for pid, ev in r1["evidence"].items():
                ev2 = r2["evidence"].get(pid)
                if ev2 is None or ev != ev2:
                    out.append(f"{qid} {s_name} 证据[{pid}] 不一致")
            if r1["metrics"] != r2["metrics"]:
                out.append(f"{qid} {s_name} 指标不一致")
            if r1["graph"] != r2["graph"]:
                out.append(f"{qid} {s_name} 图指标不一致")
    return out


def aggregate(per_q, names, truncate_frac) -> dict[str, dict[str, float]]:
    """与 run_benchmark 同口径的聚合(时延除外)。"""
    agg = {}
    for name in names:
        rows = [per_q[qid][name] for qid in per_q]
        row: dict[str, float] = {}
        for key in METRIC_KEYS:
            row[key] = mean([r["metrics"].get(key, 0.0) for r in rows])
        for key in ("similarity_calls", "index_lookups", "iterations"):
            row[key] = mean([r.get(key, 0.0) for r in rows])
        for key in GRAPH_KEYS:
            row[key] = mean([r["graph"].get(key, 0.0) for r in rows])
        if truncate_frac is not None:
            row["predictive_recall_at_k"] = mean(
                [r["metrics"].get("predictive_recall_at_k", 0.0) for r in rows]
            )
        row["early_stopped_frac"] = mean(
            [1.0 if r.get("early_stopped") else 0.0 for r in rows]
        )
        agg[name] = row
    return agg


def find_frozen(results_dir, stem, k, nq, trunc_tag):
    if trunc_tag:
        pat = f"EXP-001-{stem}-k{k}-q{nq}{trunc_tag}-*.json"
    else:
        pat = f"EXP-001-{stem}-k{k}-q{nq}-[0-9]*.json"
    cands = sorted(results_dir.glob(pat))
    return cands[-1] if cands else None


def frozen_diffs(agg, frozen_path) -> list[str]:
    data = json.loads(frozen_path.read_text(encoding="utf-8"))
    frozen = data["aggregate"]
    out = []
    for name, row in agg.items():
        for key, val in row.items():
            ref = frozen.get(name, {}).get(key)
            if ref is None:
                out.append(f"冻结[{name}][{key}] 缺失")
            elif abs(ref - val) > 1e-12:
                out.append(f"聚合 {name}.{key}: 冻结={ref} 本次={val}")
    return out


def run_comparison(
    config: str,
    queries: int,
    k: int,
    query_seed: int,
    truncate_frac: float | None,
) -> dict[str, Any]:
    cfg_path = Path(config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    corpus_cfg = SyntheticCorpusConfig(**cfg["corpus"])
    corpus = SyntheticEventCorpus(corpus_cfg)
    view = identity_view(corpus.points, corpus_cfg.index_top_m)
    nq = queries if queries > 0 else corpus_cfg.n_events
    qs = corpus.sample_queries(nq, rng_seed=query_seed, truncate_frac=truncate_frac)
    g_cfg = cfg.get("graph", {})
    direct, names = run_path(corpus, cfg["strategies"], qs, k, g_cfg, truncate_frac)
    via_view, _ = run_path(view, cfg["strategies"], qs, k, g_cfg, truncate_frac)
    diffs = path_diffs(direct, via_view)
    agg_direct = aggregate(direct, names, truncate_frac)
    agg_view = aggregate(via_view, names, truncate_frac)
    trunc_tag = "" if truncate_frac is None else f"-t{truncate_frac}"
    frozen_path = find_frozen(
        cfg_path.parents[1] / "research" / "results",
        cfg_path.stem,
        k,
        nq,
        trunc_tag,
    )
    frozen = (
        frozen_diffs(agg_direct, frozen_path)
        if frozen_path
        else ["跳过: 无冻结结果可对账"]
    )
    hard = [d for d in frozen if not d.startswith("跳过")]
    verdict = "PASS" if not diffs and not hard else "FAIL"
    return {
        "config": str(cfg_path),
        "k": k,
        "n_queries": nq,
        "query_seed": query_seed,
        "truncate_frac": truncate_frac,
        "strategy_names": names,
        "diffs": diffs,
        "frozen_diffs": frozen,
        "aggregate_direct": agg_direct,
        "aggregate_view": agg_view,
        "frozen_path": str(frozen_path) if frozen_path else None,
        "verdict": verdict,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="E1 协议层行为等价证明")
    ap.add_argument("--config", default="configs/benchmark.small.json")
    ap.add_argument("--queries", type=int, default=0, help="0 = 每事件一个查询")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--query-seed", type=int, default=1)
    ap.add_argument("--truncate", type=float, default=None)
    args = ap.parse_args()
    result = run_comparison(
        args.config, args.queries, args.k, args.query_seed, args.truncate
    )
    ts = time.strftime("%Y%m%d-%H%M%S")
    out_dir = Path(__file__).resolve().parents[1] / "research" / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"PROOF-E1-EQUIV-{ts}.json"
    out_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("=== E1 行为等价证明 ===")
    print(f"配置: {result['config']} k={result['k']} 查询数={result['n_queries']} 截断={result['truncate_frac']}")
    print(f"路径差异: {len(result['diffs'])} 处")
    for d in result["diffs"][:20]:
        print(f"  {d}")
    print(f"冻结对账: {result['frozen_path']}")
    for d in result["frozen_diffs"][:20]:
        print(f"  {d}")
    print(f"判定: {result['verdict']}")
    print(f"回执: {out_path}")
    if result["verdict"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
