"""EXP-001 Benchmark 运行脚本: A 传统 / B Anchor / C Multi-Net 对比。

用法:
    python scripts/run_benchmark.py --config configs/benchmark.small.json
    python scripts/run_benchmark.py --config configs/benchmark.medium.json --truncate 0.6

输出:
    research/results/EXP-001-<config>-<k>-<nq>[-t<trunc>]-<ts>.json
    (控制台打印汇总表与假设判定)

诚实规则(宪法第 3 条):
    - 每个策略记录 similarity_calls / index_lookups / iterations / latency_ms;
    - 索引构建成本不在查询时计数中;
    - 任何"更优"结论以 JSON 中的数字为准。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.anchors.anchor_detector import AnchorConfig  # noqa: E402
from cognitive_os.datasets.synthetic_events import SyntheticCorpusConfig, SyntheticEventCorpus  # noqa: E402
from cognitive_os.graph.evidence_graph import EvidenceGraph  # noqa: E402
from cognitive_os.metrics import rank_stats, recall_at_k, mean  # noqa: E402
from cognitive_os.nets.search_net import SearchNetConfig  # noqa: E402
from cognitive_os.retrieval.strategy_a_traditional import TraditionalRetrieval  # noqa: E402
from cognitive_os.retrieval.strategy_b_anchor import AnchorRetrieval  # noqa: E402
from cognitive_os.retrieval.strategy_c_multinet import DynamicMultiNetRetrieval  # noqa: E402
from cognitive_os.types import Query, RetrievalResult  # noqa: E402
from cognitive_os.validation.progressive import ValidatorConfig  # noqa: E402


def build_strategies(corpus: SyntheticEventCorpus, s_cfg: Dict[str, Any]):
    a_cfg = s_cfg["A"]
    a = TraditionalRetrieval(corpus, source_bonus=a_cfg.get("source_bonus", 0.05))

    b_cfg = s_cfg["B"]
    b = AnchorRetrieval(
        corpus,
        anchor_cfg=AnchorConfig(**b_cfg["anchor"]),
        net_cfg=SearchNetConfig(**b_cfg["net"]),
    )

    c_cfg = s_cfg["C"]
    c = DynamicMultiNetRetrieval(
        corpus,
        net_configs=[SearchNetConfig(**n) for n in c_cfg["nets"]],
        validator_cfg=ValidatorConfig(**c_cfg["validator"]),
    )
    return [a, b, c]


def graph_metrics(
    corpus: SyntheticEventCorpus,
    result: RetrievalResult,
    g_cfg: Dict[str, Any],
    relevant: set,
    seed_pids: List[str],
) -> Dict[str, float]:
    """对"种子 + top-k"建多信号图与纯语义图, 返回成分纯度与重建 F1。

    种子必须纳入图中: 否则种子的连通成分退化为孤立点(伪 1.0 纯度)。
    """
    candidates = list(result.ranked_pids)
    for s in seed_pids:
        if s not in candidates:
            candidates.append(s)
    if not candidates:
        return {"purity": 0.0, "recon_f1": 0.0, "purity_semantic_only": 0.0}

    multi = EvidenceGraph.build(
        corpus,
        candidates,
        semantic_threshold=g_cfg["semantic_threshold"],
        temporal_window=g_cfg.get("temporal_window"),
        require_source_diversity=g_cfg.get("require_source_diversity", False),
    )
    comp = multi.component_of(seed_pids[0])
    purity = multi.cluster_purity(comp, {p: corpus.event_of(p) for p in comp})
    recon = multi.reconstruction(comp, relevant)

    semantic_only = EvidenceGraph.build(
        corpus,
        candidates,
        semantic_threshold=g_cfg["semantic_threshold"],
        temporal_window=None,
        require_source_diversity=False,
    )
    comp_s = semantic_only.component_of(seed_pids[0])
    purity_sem = semantic_only.cluster_purity(
        comp_s, {p: corpus.event_of(p) for p in comp_s}
    )
    return {
        "purity": purity,
        "recon_f1": recon["f1"],
        "purity_semantic_only": purity_sem,
    }


def run_one(
    corpus: SyntheticEventCorpus,
    strategy,
    query: Query,
    k: int,
    g_cfg: Dict[str, Any],
    truncate_frac: Optional[float],
    relevant_observed: set,
    future: set,
) -> Dict[str, Any]:
    res = strategy.retrieve(query, k)
    d = res.as_dict()
    d["metrics"] = rank_stats(res.ranked_pids, relevant_observed, k)
    d["graph"] = graph_metrics(corpus, res, g_cfg, relevant_observed, query.seed_pids)

    if truncate_frac is not None and future:
        # 预测性指标: 用全索引重跑(无 allowed 限制), 度量"未观测碎片
        # 是否已被排在 top-k"——即结构是否被提前识别。见 BM-001 §3 局限。
        full_query = Query(qid=query.qid, seed_pids=query.seed_pids, event_id=query.event_id)
        res_full = strategy.retrieve(full_query, k)
        d["metrics"]["predictive_recall_at_k"] = recall_at_k(res_full.ranked_pids, future, k)
    return d


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-001 Dynamic Nets vs Baseline benchmark")
    ap.add_argument("--config", default="configs/benchmark.small.json")
    ap.add_argument("--queries", type=int, default=0, help="0 = 每事件一个查询")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--truncate", type=float, default=None, help="0-1: 查询时刻 = 事件开始 + frac×跨度")
    ap.add_argument("--query-seed", type=int, default=1)
    ap.add_argument("--out", default=None, help="输出 JSON 路径(默认 research/results/)")
    args = ap.parse_args()

    cfg_path = Path(args.config)
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    corpus_cfg = SyntheticCorpusConfig(**cfg["corpus"])
    corpus = SyntheticEventCorpus(corpus_cfg)

    n_events = corpus_cfg.n_events
    nq = args.queries if args.queries > 0 else n_events
    queries = corpus.sample_queries(nq, rng_seed=args.query_seed, truncate_frac=args.truncate)
    strategies = build_strategies(corpus, cfg["strategies"])
    g_cfg = cfg.get("graph", {})

    per_query: Dict[str, Dict[str, Any]] = {}
    for q in queries:
        event_pids = set(corpus.event_fragments(q.event_id))
        # 相关集排除种子自身: 种子不可检索, 否则 Recall 分母虚高
        relevant_observed = {p for p in event_pids if q.is_allowed(p)} - set(q.seed_pids)
        future = {p for p in event_pids if not q.is_allowed(p)} if args.truncate is not None else set()
        per_query[q.qid] = {
            "event_id": q.event_id,
            "seed": q.seed_pids,
            "strategies": {
                s.name: run_one(corpus, s, q, args.k, g_cfg, args.truncate, relevant_observed, future)
                for s in strategies
            },
        }

    # 聚合
    agg: Dict[str, Dict[str, float]] = {}
    metric_keys = [
        "precision_at_k", "recall_at_k", "f1_at_k", "ndcg_at_k", "mrr",
    ]
    eff_keys = ["similarity_calls", "index_lookups", "iterations", "latency_ms"]
    graph_keys = ["purity", "recon_f1", "purity_semantic_only"]
    for s in strategies:
        rows = [per_query[q.qid]["strategies"][s.name] for q in queries]
        agg[s.name] = {
            key: mean([r["metrics"].get(key, 0.0) for r in rows])
            for key in metric_keys
        }
        agg[s.name].update({
            key: mean([r.get(key, 0.0) for r in rows])
            for key in eff_keys
        })
        agg[s.name].update({
            key: mean([r["graph"].get(key, 0.0) for r in rows])
            for key in graph_keys
        })
        if args.truncate is not None:
            agg[s.name]["predictive_recall_at_k"] = mean(
                [r["metrics"].get("predictive_recall_at_k", 0.0) for r in rows]
            )
        agg[s.name]["early_stopped_frac"] = mean(
            [1.0 if r.get("early_stopped") else 0.0 for r in rows]
        )

    # 假设判定(BM-001 §5)
    A, B, C = agg["A-traditional"], agg["B-anchor"], agg["C-multinet"]
    judgements = {}
    b_saves = A["similarity_calls"] > 0 and B["similarity_calls"] < 0.5 * A["similarity_calls"]
    b_recall_loss = A["recall_at_k"] - B["recall_at_k"]
    judgements["H-001_anchor_efficiency"] = (
        "PASS" if (b_saves and b_recall_loss <= 0.10) else "FAIL"
    )
    judgements["H-002_multinet_quality"] = (
        "PASS" if (C["f1_at_k"] >= A["f1_at_k"] - 1e-9 and C["early_stopped_frac"] > 0.0) else "FAIL"
    )
    judgements["H-002_predictive_recall"] = (
        "PASS"
        if (args.truncate is not None and C["predictive_recall_at_k"] > A["predictive_recall_at_k"])
        else ("FAIL" if args.truncate is not None else "N/A")
    )
    judgements["H-003_structure_consistency"] = (
        "PASS"
        if (C["purity"] > C["purity_semantic_only"] or B["purity"] > B["purity_semantic_only"])
        else "FAIL"
    )

    # 输出
    ts = time.strftime("%Y%m%d-%H%M%S")
    tag = f"{cfg_path.stem}-k{args.k}-q{nq}"
    if args.truncate is not None:
        tag += f"-t{args.truncate}"
    out = Path(args.out) if args.out else Path(__file__).resolve().parents[1] / "research" / "results"
    out.mkdir(parents=True, exist_ok=True)
    out_path = out / f"EXP-001-{tag}-{ts}.json"
    payload = {
        "meta": {
            "config": str(cfg_path),
            "k": args.k,
            "n_queries": nq,
            "truncate_frac": args.truncate,
            "query_seed": args.query_seed,
            "corpus_seed": corpus_cfg.seed,
            "timestamp": ts,
        },
        "corpus_stats": corpus.similarity_stats(),
        "per_query": per_query,
        "aggregate": agg,
        "judgements": judgements,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    # 控制台
    print(f"\n=== EXP-001 {cfg_path.name} k={args.k} nq={nq} truncate={args.truncate} ===")
    print(f"corpus: within_mean={corpus.similarity_stats()['within_mean']:.3f} "
          f"cross_mean={corpus.similarity_stats()['cross_mean']:.3f}")
    hdr = ["strategy", "P@k", "R@k", "F1@k", "NDCG", "MRR", "sim_calls", "iters", "ms", "purity", "reconF1"]
    if args.truncate is not None:
        hdr.append("predR")
    print("  ".join(f"{h:>10}" for h in hdr))
    for s in strategies:
        a = agg[s.name]
        row = [s.name, f"{a['precision_at_k']:.3f}", f"{a['recall_at_k']:.3f}", f"{a['f1_at_k']:.3f}",
               f"{a['ndcg_at_k']:.3f}", f"{a['mrr']:.3f}", f"{a['similarity_calls']:.0f}",
               f"{a['iterations']:.1f}", f"{a['latency_ms']:.2f}", f"{a['purity']:.3f}", f"{a['recon_f1']:.3f}"]
        if args.truncate is not None:
            row.append(f"{a['predictive_recall_at_k']:.3f}")
        print("  ".join(f"{c:>10}" for c in row))
    print(f"early_stopped_frac: A={agg['A-traditional']['early_stopped_frac']:.2f} "
          f"B={agg['B-anchor']['early_stopped_frac']:.2f} "
          f"C={agg['C-multinet']['early_stopped_frac']:.2f}")
    print(f"purity_semantic_only: A={agg['A-traditional']['purity_semantic_only']:.3f} "
          f"B={agg['B-anchor']['purity_semantic_only']:.3f} "
          f"C={agg['C-multinet']['purity_semantic_only']:.3f}")
    print("\njudgements:")
    for kk, v in judgements.items():
        print(f"  {kk}: {v}")
    print(f"\n原始数据: {out_path}")


if __name__ == "__main__":
    main()
