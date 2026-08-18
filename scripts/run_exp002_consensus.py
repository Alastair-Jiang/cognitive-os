"""EXP-002 诊断: C 策略共识聚合方式对比(max vs mean)。

问题(EXP-001 解释第 3 条): C 的跨网共识被"高分单网候选"主导?
当前 ValidatorConfig.aggregation="max"(最强网说了算);
本脚本对比 "mean"(各网平均发言) 是否改善 C 的 F1/MRR 与稳定性。

用法:
    python scripts/run_exp002_consensus.py [--config configs/benchmark.small.json]
                                          [--config configs/benchmark.medium.json ...]

输出:
    research/results/EXP-002-consensus-<config>-<ts>.json + 控制台对比表
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

from cognitive_os.datasets.synthetic_events import SyntheticCorpusConfig, SyntheticEventCorpus  # noqa: E402
from cognitive_os.nets.search_net import SearchNetConfig  # noqa: E402
from cognitive_os.retrieval.strategy_c_multinet import DynamicMultiNetRetrieval  # noqa: E402
from cognitive_os.validation.progressive import ValidatorConfig  # noqa: E402
from cognitive_os.metrics import mean  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_benchmark import run_one  # noqa: E402

GRAPH_CFG: Dict[str, Any] = {
    "semantic_threshold": 0.68,
    "temporal_window": 40.0,
    "require_source_diversity": True,
}


def run_c_with_aggregation(
    corpus: SyntheticEventCorpus,
    c_cfg: Dict[str, Any],
    queries,
    k: int,
    aggregation: str,
) -> Dict[str, Dict[str, float]]:
    validator_cfg = ValidatorConfig(**c_cfg["validator"])
    validator_cfg.aggregation = aggregation
    strategy = DynamicMultiNetRetrieval(
        corpus,
        net_configs=[SearchNetConfig(**n) for n in c_cfg["nets"]],
        validator_cfg=validator_cfg,
    )
    per_q: Dict[str, Dict[str, Any]] = {}
    for q in queries:
        event_pids = set(corpus.event_fragments(q.event_id))
        relevant_observed = {p for p in event_pids if q.is_allowed(p)} - set(q.seed_pids)
        res = strategy.retrieve(q, k)
        d = res.as_dict()
        d["metrics"] = __import__("cognitive_os.metrics", fromlist=["rank_stats"]).rank_stats(
            res.ranked_pids, relevant_observed, k
        )
        per_q[q.qid] = d

    keys = ["f1_at_k", "recall_at_k", "precision_at_k", "mrr", "similarity_calls",
            "iterations", "latency_ms"]
    agg: Dict[str, float] = {}
    for key in keys:
        if key in ("latency_ms", "iterations", "similarity_calls"):
            agg[key] = mean([per_q[q.qid][key] for q in queries])
        else:
            agg[key] = mean([per_q[q.qid]["metrics"][key] for q in queries])
    agg["early_stopped_frac"] = mean(
        [1.0 if per_q[q.qid].get("early_stopped") else 0.0 for q in queries]
    )
    return agg


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-002 C 策略共识聚合 max vs mean 诊断")
    ap.add_argument("--config", action="append", default=[])
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--queries", type=int, default=0)
    ap.add_argument("--truncate", type=float, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    configs = args.config or ["configs/benchmark.small.json", "configs/benchmark.medium.json"]
    reports: List[Dict[str, Any]] = []

    for cfg_rel in configs:
        cfg_path = root / cfg_rel
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        corpus = SyntheticEventCorpus(SyntheticCorpusConfig(**cfg["corpus"]))
        n_events = cfg["corpus"]["n_events"]
        nq = args.queries if args.queries > 0 else n_events
        queries = corpus.sample_queries(nq, rng_seed=1, truncate_frac=args.truncate)
        c_cfg = cfg["strategies"]["C"]

        rows: Dict[str, Dict[str, float]] = {}
        for agg in ("max", "mean"):
            rows[agg] = run_c_with_aggregation(corpus, c_cfg, queries, args.k, agg)

        report = {
            "config": cfg_rel,
            "n_queries": nq,
            "truncate": args.truncate,
            "max": {k_: round(v, 4) for k_, v in rows["max"].items()},
            "mean": {k_: round(v, 4) for k_, v in rows["mean"].items()},
            "delta_mean_minus_max": {
                k_: round(rows["mean"][k_] - rows["max"][k_], 4)
                for k_ in rows["max"]
            },
        }
        reports.append(report)

        print(f"\n=== consensus 诊断 {cfg_rel} k={args.k} nq={nq} truncate={args.truncate} ===")
        hdr = ["metric", "max", "mean", "delta"]
        print("  ".join(f"{h:>14}" for h in hdr))
        for metric in ["f1_at_k", "recall_at_k", "precision_at_k", "mrr",
                       "similarity_calls", "iterations", "latency_ms", "early_stopped_frac"]:
            row = [metric, f"{report['max'][metric]:.4f}", f"{report['mean'][metric]:.4f}",
                   f"{report['delta_mean_minus_max'][metric]:+.4f}"]
            print("  ".join(f"{v:>14}" for v in row))

    ts = time.strftime("%Y%m%d-%H%M%S")
    out = Path(args.out) if args.out else root / "research" / "results"
    out.mkdir(parents=True, exist_ok=True)
    out_path = out / f"EXP-002-consensus-{'-'.join(Path(c).stem for c in configs)}-{ts}.json"
    out_path.write_text(
        json.dumps({"meta": {"experiment": "EXP-002-consensus", "timestamp": ts},
                    "reports": reports}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n原始数据: {out_path}")


if __name__ == "__main__":
    main()