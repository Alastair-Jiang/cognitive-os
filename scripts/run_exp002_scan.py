"""EXP-002 歧义档位扫描: noise/主题重叠 × 三策略, 检验 H-001 召回损失曲线。

用法:
    python scripts/run_exp002_scan.py [--k 10] [--queries 0] [--out research/results]

设计(预注册, 见 research/benchmarks/BM-001 §5 扩展):
- 固定基础结构: n_events=12, fragments_per_event=8, embed_dim=24, n_topics=5,
  seed=20260819(与 small 配置一致), 只变两个歧义轴:
    * 主题重叠: topics_per_event ∈ {2, 4, 5}(n_topics=5 → 40% / 80% / 100% 重叠)
    * 事件内噪声: within_event_noise ∈ {0.15, 0.3, 0.5}(低 / 中 / 高)
- 歧义度以语料可观测统计为准: margin = within_mean - cross_mean
  (margin 小 = 同/跨事件更难区分 = 歧义高) + cross_max(最危险歧义对)
- 每档: 每事件 1 查询(同 seed), k=10, A/B/C 三策略同查询同 k(不针对档位调参)
- H-001 判定(每档): B sim_calls < 0.5 × A 且 Recall 损失 ≤ 10pp
- 输出: research/results/EXP-002-scan-<ts>.json(全量) + 控制台汇总表

诚实规则(宪法第 3 条): 所有数字以 JSON 为准; 判定失败如实报告。
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.anchors.anchor_detector import AnchorConfig  # noqa: E402
from cognitive_os.datasets.synthetic_events import (  # noqa: E402
    SyntheticCorpusConfig,
    SyntheticEventCorpus,
)
from cognitive_os.metrics import mean  # noqa: E402
from cognitive_os.nets.search_net import SearchNetConfig  # noqa: E402
from cognitive_os.retrieval.strategy_a_traditional import TraditionalRetrieval  # noqa: E402
from cognitive_os.retrieval.strategy_b_anchor import AnchorRetrieval  # noqa: E402
from cognitive_os.retrieval.strategy_c_multinet import DynamicMultiNetRetrieval  # noqa: E402
from cognitive_os.validation.progressive import ValidatorConfig  # noqa: E402

# 从 run_benchmark.py 复用策略构建(同一份代码, 保证口径一致)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_benchmark import run_one  # noqa: E402

STRATEGY_KEYS = ["A-traditional", "B-anchor", "C-multinet"]


def build_strategies(corpus: SyntheticEventCorpus, s_cfg: dict[str, Any]):
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


# 策略参数: 复用 medium 档的锚点/网配置(比 small 更接近"可用"档位),
# 并在所有扫描档位上固定不变(防止"每档调参"的口径作弊)。
SCAN_STRATEGY_TEMPLATE: dict[str, Any] = {
    "A": {"source_bonus": 0.05},
    "B": {
        "anchor": {
            "n_anchors": 4, "pool_hops": 1,
            "semantic_w": 1.0, "source_w": 0.5, "temporal_w": 0.3,
            "density_w": 0.4, "temporal_scale": 40.0,
        },
        "net": {
            "name": "B-expansion", "radius": 0.7, "temporal_window": 40.0,
            "source_min_weight": 0.0, "max_candidates_per_anchor": 6,
            "max_hops": 1, "semantic_w": 1.0, "source_w": 0.3,
            "temporal_w": 0.2, "structural_w": 0.2,
        },
    },
    "C": {
        "validator": {
            "confidence_threshold": 0.9, "stabilization_eps": 0.001,
            "stabilize_rounds": 2, "max_rounds": 8, "consensus_w": 0.4,
        },
        "nets": [
            {"name": "narrow-semantic", "radius": 0.88, "temporal_window": None,
             "source_min_weight": 0.0, "max_candidates_per_anchor": 4,
             "max_hops": 1, "semantic_w": 1.0, "source_w": 0.0,
             "temporal_w": 0.0, "structural_w": 0.0},
            {"name": "wide-source", "radius": 0.68, "temporal_window": 40.0,
             "source_min_weight": 0.0, "max_candidates_per_anchor": 8,
             "max_hops": 2, "semantic_w": 0.5, "source_w": 0.4,
             "temporal_w": 0.1, "structural_w": 0.2},
            {"name": "temporal", "radius": 0.76, "temporal_window": 25.0,
             "source_min_weight": 0.0, "max_candidates_per_anchor": 6,
             "max_hops": 2, "semantic_w": 0.6, "source_w": 0.1,
             "temporal_w": 0.3, "structural_w": 0.2},
            {"name": "structural", "radius": 0.7, "temporal_window": 50.0,
             "source_min_weight": 0.0, "max_candidates_per_anchor": 6,
             "max_hops": 3, "semantic_w": 0.4, "source_w": 0.2,
             "temporal_w": 0.1, "structural_w": 0.5},
        ],
    },
}

GRAPH_CFG: dict[str, Any] = {
    "semantic_threshold": 0.68,
    "temporal_window": 40.0,
    "require_source_diversity": True,
}

def grid_corpus_config(
    topics_per_event: int,
    within_event_noise: float,
    seed: int,
) -> SyntheticCorpusConfig:
    """EXP-002 网格格点语料配置(单一事实来源; EXP-004a 复用, D-5)。"""
    return SyntheticCorpusConfig(
        n_events=12,
        fragments_per_event=8,
        embed_dim=24,
        n_topics=N_TOPICS,
        topics_per_event=topics_per_event,
        within_event_noise=within_event_noise,
        time_horizon=100.0,
        event_span=20.0,
        source_count=4,
        source_min_weight=0.6,
        primary_source_prob=0.6,
        index_top_m=6,
        seed=seed,
    )


# 歧义轴网格
N_TOPICS = 5
OVERLAP_LEVELS: list[tuple[str, int]] = [
    ("overlap-low", 2),    # 40% 主题共享
    ("overlap-mid", 4),    # 80% 主题共享
    ("overlap-high", 5),   # 100% 主题共享(全共享 → 事件只靠权重/噪声区分)
]
NOISE_LEVELS: list[tuple[str, float]] = [
    ("noise-low", 0.15),
    ("noise-mid", 0.30),
    ("noise-high", 0.50),  # 与 small 默认一致
]


def run_cell(
    label: str,
    topics_per_event: int,
    within_event_noise: float,
    k: int,
    nq: int,
    query_seed: int,
) -> dict[str, Any]:
    """跑一个歧义档位(一个小型完整 benchmark)。"""
    corpus_cfg = grid_corpus_config(topics_per_event, within_event_noise, 20260819)
    corpus = SyntheticEventCorpus(corpus_cfg)
    strategies = build_strategies(corpus, SCAN_STRATEGY_TEMPLATE)

    queries = corpus.sample_queries(nq, rng_seed=query_seed)
    per_query: dict[str, dict[str, Any]] = {}
    for q in queries:
        event_pids = set(corpus.event_fragments(q.event_id))
        relevant_observed = {p for p in event_pids if q.is_allowed(p)} - set(q.seed_pids)
        per_query[q.qid] = {
            "event_id": q.event_id,
            "seed": q.seed_pids,
            "strategies": {
                s.name: run_one(
                    corpus, s, q, k, GRAPH_CFG, None, relevant_observed, set()
                )
                for s in strategies
            },
        }

    agg: dict[str, dict[str, float]] = {}
    for s in strategies:
        rows = [per_query[q.qid]["strategies"][s.name] for q in queries]
        agg[s.name] = {
            "f1_at_k": mean([r["metrics"]["f1_at_k"] for r in rows]),
            "recall_at_k": mean([r["metrics"]["recall_at_k"] for r in rows]),
            "precision_at_k": mean([r["metrics"]["precision_at_k"] for r in rows]),
            "mrr": mean([r["metrics"]["mrr"] for r in rows]),
            "similarity_calls": mean([r["similarity_calls"] for r in rows]),
            "iterations": mean([r["iterations"] for r in rows]),
            "early_stopped_frac": mean([1.0 if r.get("early_stopped") else 0.0 for r in rows]),
            "purity": mean([r["graph"]["purity"] for r in rows]),
            "recon_f1": mean([r["graph"]["recon_f1"] for r in rows]),
        }

    stats = corpus.similarity_stats()
    margin = stats["within_mean"] - stats["cross_mean"]
    A, B, C = agg["A-traditional"], agg["B-anchor"], agg["C-multinet"]
    recall_loss = A["recall_at_k"] - B["recall_at_k"]
    sim_saving = B["similarity_calls"] / max(A["similarity_calls"], 1e-9)
    h001_reviewable = (
        A["similarity_calls"] > 0 and B["similarity_calls"] < 0.5 * A["similarity_calls"]
    )
    h001 = "PASS" if (h001_reviewable and recall_loss <= 0.10) else "FAIL"

    return {
        "cell": label,
        "params": {
            "topics_per_event": topics_per_event,
            "within_event_noise": within_event_noise,
            "n_topics": N_TOPICS,
            "n_events": 12,
            "fragments_per_event": 8,
            "seed": 20260819,
        },
        "ambiguity": {
            "within_mean": stats["within_mean"],
            "cross_mean": stats["cross_mean"],
            "margin": margin,
            "cross_max": stats["cross_max"],
        },
        "A": {k_: round(v, 4) for k_, v in A.items()},
        "B": {k_: round(v, 4) for k_, v in B.items()},
        "C": {k_: round(v, 4) for k_, v in C.items()},
        "h001": {
            "recall_loss_pp": round((A["recall_at_k"] - B["recall_at_k"]) * 100, 1),
            "sim_ratio_B_over_A": round(sim_saving, 2),
            "judgement": h001,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-002 歧义档位扫描")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--queries", type=int, default=12)
    ap.add_argument("--query-seed", type=int, default=1)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    cells: list[dict[str, Any]] = []
    for ov_label, tpe in OVERLAP_LEVELS:
        for nz_label, noise in NOISE_LEVELS:
            label = f"{ov_label}-{nz_label}"
            print(f"[scan] {label}: tpe={tpe} noise={noise} …", flush=True)
            cells.append(
                run_cell(label, tpe, noise, args.k, args.queries, args.query_seed)
            )

    # 汇总输出
    ts = time.strftime("%Y%m%d-%H%M%S")
    default_out = Path(__file__).resolve().parents[1] / "research" / "results"
    out = Path(args.out) if args.out else default_out
    out.mkdir(parents=True, exist_ok=True)
    out_path = out / f"EXP-002-scan-k{args.k}-q{args.queries}-{ts}.json"
    payload = {
        "meta": {
            "experiment": "EXP-002",
            "k": args.k,
            "n_queries": args.queries,
            "query_seed": args.query_seed,
            "strategy_template": "medium-scale fixed (no per-cell tuning)",
            "timestamp": ts,
        },
        "cells": cells,
    }
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n=== EXP-002 歧义档位扫描汇总 ===")
    hdr = ["cell", "margin", "crossMax", "A F1", "B F1", "B R-loss", "B/A sim", "H-001"]
    print("  ".join(f"{h:>12}" for h in hdr))
    for c in cells:
        row = [
            c["cell"],
            f"{c['ambiguity']['margin']:.3f}",
            f"{c['ambiguity']['cross_max']:.3f}",
            f"{c['A']['f1_at_k']:.3f}",
            f"{c['B']['f1_at_k']:.3f}",
            f"{c['h001']['recall_loss_pp']:.1f}pp",
            f"{c['h001']['sim_ratio_B_over_A']:.2f}",
            c["h001"]["judgement"],
        ]
        print("  ".join(f"{v:>12}" for v in row))
    print(f"\n原始数据: {out_path}")


if __name__ == "__main__":
    main()
