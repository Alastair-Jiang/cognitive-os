"""EXP-002 H-003 重设计: 聚类级纯度 + 因果/引用结构信号。

EXP-001 的 H-003 测量失败原因(诊断, 见 EXP-001 文档):
1. 只测种子所在成分(event purity) → 遗漏其他成分的拆分质量;
2. 合成语料没有真正的结构信号(来源信号在合成设置中信息量弱)
   → 结构一致性没有发挥空间。

本实验重设计:
- 语料: 事件组织成 K 条因果链(causal_chains), 链内相邻事件碎片互相
  "提及"(meta.mentions)——真实、与语义独立的引用结构;
- 指标:
  * 聚类级事件纯度 mean_component_purity(全部成分, 按大小加权);
  * 聚类级链纯度 mean_chain_purity(成分内最大链占比——结构信号
    是否把因果链聚合起来);
  * 种子成分纯度(保留 EXP-001 口径对比);
- 建图模式对比:
  * semantic-only: 纯语义阈值;
  * multi-signal: 语义+时间+来源多样性(EXP-001 的"多信号图");
  * +causal: 上述基础上加引用边(硬结构信号, 不依赖语义阈值)。
- 两个层面:
  * 检索层: 在 A/B/C 三策略 top-k 候选上建图;
  * 全量层: 对全部语料点建图(与检索解耦, 直接检验"结构一致性
    ≠ 语义相似度"——H-003 的核心命题)。

判定(预注册):
- H-003 新表述: 带因果结构的语料上, +causal 图的全量聚类级链纯度
  显著高于 semantic-only 图(Δ ≥ 0.10), 且事件级纯度不劣化超过 0.10。
- 任何方向都如实记录, 不为了支持假设而挑选口径。

用法:
    python scripts/run_exp002_h003.py [--k 10] [--out research/results]
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

from cognitive_os.datasets.synthetic_events import (  # noqa: E402
    SyntheticCorpusConfig,
    SyntheticEventCorpus,
)
from cognitive_os.graph.evidence_graph import EvidenceGraph  # noqa: E402
from cognitive_os.metrics import (  # noqa: E402
    mean,
    mean_chain_purity,
    mean_component_purity,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_benchmark import build_strategies  # noqa: E402

GRAPH_MODES: list[tuple[str, dict[str, Any]]] = [
    ("semantic-only", {"semantic_threshold": 0.68, "temporal_window": None,
                       "require_source_diversity": False, "causal_edges": False}),
    ("multi-signal", {"semantic_threshold": 0.68, "temporal_window": 40.0,
                      "require_source_diversity": True, "causal_edges": False}),
    ("+causal", {"semantic_threshold": 0.68, "temporal_window": 40.0,
                 "require_source_diversity": True, "causal_edges": True}),
]

# 全量层阈值扫描: 语义阈值越紧, 纯语义图越碎, 引用边越有发挥空间
FULL_LAYER_THRESHOLDS = [0.68, 0.78, 0.85]
# 主判定阈值(预注册): 0.85 下纯语义图应已碎裂(事件级簇), 引用边的
# 链恢复价值应显现; 0.68 是 EXP-001 口径的地板参照(预期全连接失效)
JUDGEMENT_THRESHOLD = 0.85

CORPUS_CFG = dict(
    n_events=12,
    fragments_per_event=8,
    embed_dim=24,
    n_topics=5,
    topics_per_event=4,
    within_event_noise=0.3,
    time_horizon=100.0,
    event_span=20.0,
    source_count=4,
    source_min_weight=0.6,
    primary_source_prob=0.6,
    index_top_m=6,
    causal_chains=3,
    mention_prob=0.4,
    seed=20260819,
)


def graph_analysis(
    corpus: SyntheticEventCorpus,
    candidate_pids: list[str],
) -> dict[str, dict[str, float]]:
    """对同一候选集, 用三种模式建图, 返回聚类级指标。"""
    pid_to_event = {p: corpus.event_of(p) for p in candidate_pids}
    pid_to_chain = {p: corpus.chain_of(p) for p in candidate_pids}
    out: dict[str, dict[str, float]] = {}
    for mode, kw in GRAPH_MODES:
        g = EvidenceGraph.build(corpus, candidate_pids, **kw)
        comps = g.components()
        # 孤立点也应计入(它们也是成分)
        seen = set()
        for c in comps:
            seen.update(c)
        for p in candidate_pids:
            if p not in seen:
                comps.append([p])
        out[mode] = {
            "mean_event_purity": mean_component_purity(comps, pid_to_event),
            "mean_chain_purity": mean_chain_purity(comps, pid_to_chain),
            "n_components": len(comps),
            "n_edges": len(g.edges),
        }
    return out


def chain_connectivity(corpus: SyntheticEventCorpus, components) -> float:
    """链连通率(辅助分析, 非主判定): 链内碎片对在同一成分的平均比例。

    测的是“结构信号把传播链连起来”的能力——纯度测排他性, 连通性
    测的是“链是否被恢复”。范围 [0,1] 越高越好。
    """
    chain_frags: dict[int, list[str]] = {}
    for p in corpus.point_ids:
        cid = corpus.chain_of(p)
        if cid >= 0:
            chain_frags.setdefault(cid, []).append(p)
    comp_of: dict[str, int] = {}
    for ci, comp in enumerate(components):
        for p in comp:
            comp_of[p] = ci
    scores = []
    for cid, frags in chain_frags.items():
        n = len(frags)
        if n < 2:
            continue
        same = sum(1 for i in range(n) for j in range(i + 1, n)
                   if comp_of.get(frags[i]) == comp_of.get(frags[j]))
        total = n * (n - 1) / 2
        scores.append(same / total)
    return mean(scores) if scores else 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description="EXP-002 H-003 测量重设计")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--queries", type=int, default=12)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    corpus = SyntheticEventCorpus(SyntheticCorpusConfig(**CORPUS_CFG))
    stats = corpus.similarity_stats()
    print(f"corpus: within_mean={stats['within_mean']:.3f} cross_mean={stats['cross_mean']:.3f} "
          f"| chains=3 mention_prob=0.4")

    # 全量层: 与检索解耦, 直接检验结构建图能力(阈值扫描)
    all_pids = corpus.point_ids
    print("\n=== 全量层(所有语料点建图) — H-003 核心检验(阈值扫描) ===")
    full = {}
    for thr in FULL_LAYER_THRESHOLDS:
        modes = []
        for mode, kw in GRAPH_MODES:
            kw = dict(kw, semantic_threshold=thr)
            modes.append((mode, kw))
        pid_to_event = {p: corpus.event_of(p) for p in all_pids}
        pid_to_chain = {p: corpus.chain_of(p) for p in all_pids}
        row = {}
        for mode, kw in modes:
            g = EvidenceGraph.build(corpus, all_pids, **kw)
            comps = g.components()
            seen = set()
            for c in comps:
                seen.update(c)
            for p in all_pids:
                if p not in seen:
                    comps.append([p])
            row[mode] = {
                "mean_event_purity": mean_component_purity(comps, pid_to_event),
                "mean_chain_purity": mean_chain_purity(comps, pid_to_chain),
                "chain_connectivity": chain_connectivity(corpus, comps),
                "n_components": len(comps),
                "n_edges": len(g.edges),
            }
        full[str(thr)] = row
        for mode, m in row.items():
            print(f"  thr={thr} {mode:>14}: event_purity={m['mean_event_purity']:.3f} "
                  f"chain_purity={m['mean_chain_purity']:.3f} "
                  f"conn={m['chain_connectivity']:.3f} "
                  f"edges={m['n_edges']:>3} comps={m['n_components']}")

    # 检索层: A/B/C 的 top-k 候选
    cfg_json = {
        "strategies": {
            "A": {"source_bonus": 0.05},
            "B": {"anchor": {"n_anchors": 4, "pool_hops": 1, "semantic_w": 1.0,
                             "source_w": 0.5, "temporal_w": 0.3, "density_w": 0.4,
                             "temporal_scale": 40.0},
                  "net": {"name": "B-expansion", "radius": 0.7, "temporal_window": 40.0,
                          "source_min_weight": 0.0, "max_candidates_per_anchor": 6,
                          "max_hops": 1, "semantic_w": 1.0, "source_w": 0.3,
                          "temporal_w": 0.2, "structural_w": 0.2}},
            "C": {"validator": {"confidence_threshold": 0.9, "stabilization_eps": 0.001,
                                "stabilize_rounds": 2, "max_rounds": 8, "consensus_w": 0.4},
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
                  ]},
        },
    }
    strategies = build_strategies(corpus, cfg_json["strategies"])
    queries = corpus.sample_queries(args.queries, rng_seed=1)

    per_strategy: dict[str, dict[str, Any]] = {}
    for s in strategies:
        cands_per_query: list[list[str]] = []
        f1s: list[float] = []
        for q in queries:
            res = s.retrieve(q, args.k)
            event_pids = set(corpus.event_fragments(q.event_id))
            relevant = {p for p in event_pids if q.is_allowed(p)} - set(q.seed_pids)
            from cognitive_os.metrics import rank_stats
            f1s.append(rank_stats(res.ranked_pids, relevant, args.k)["f1_at_k"])
            cands = list(res.ranked_pids)
            for seed in q.seed_pids:
                if seed not in cands:
                    cands.append(seed)
            cands_per_query.append(cands)

        # 聚合: 平均每查询候选集的三模式指标(取平均)
        per_mode: dict[str, dict[str, float]] = {m: {"event_purity": [], "chain_purity": []}
                                                 for m, _ in GRAPH_MODES}
        for cands in cands_per_query:
            for mode, _ in GRAPH_MODES:
                pid_to_event = {p: corpus.event_of(p) for p in cands}
                pid_to_chain = {p: corpus.chain_of(p) for p in cands}
                g = EvidenceGraph.build(corpus, cands, **_GRAPH_MODE_KW(mode))
                comps = g.components()
                seen = set()
                for c in comps:
                    seen.update(c)
                for p in cands:
                    if p not in seen:
                        comps.append([p])
                per_mode[mode]["event_purity"].append(mean_component_purity(comps, pid_to_event))
                per_mode[mode]["chain_purity"].append(mean_chain_purity(comps, pid_to_chain))
        per_strategy[s.name] = {
            "f1_at_k": round(mean(f1s), 4),
            "modes": {
                mode: {
                    "event_purity": round(mean(vals["event_purity"]), 4),
                    "chain_purity": round(mean(vals["chain_purity"]), 4),
                }
                for mode, vals in per_mode.items()
            },
        }

    print("\n=== 检索层(A/B/C top-k 候选上建图) ===")
    for name, data in per_strategy.items():
        print(f"  {name:>12} F1@k={data['f1_at_k']:.3f}")
        for mode, m in data["modes"].items():
            print(f"      {mode:>14}: event_purity={m['event_purity']:.3f} "
                  f"chain_purity={m['chain_purity']:.3f}")

    # 判定(H-003 新表述, 预注册主阈值)
    s_f = full[str(JUDGEMENT_THRESHOLD)]["semantic-only"]
    c_f = full[str(JUDGEMENT_THRESHOLD)]["+causal"]
    delta_chain = c_f["mean_chain_purity"] - s_f["mean_chain_purity"]
    delta_event = c_f["mean_event_purity"] - s_f["mean_event_purity"]
    h003 = "PASS" if (delta_chain >= 0.10 and delta_event >= -0.10) else "FAIL"
    print("\n=== H-003 判定(全量层, 预注册主阈值 "
          f"semantic_threshold={JUDGEMENT_THRESHOLD}) ===")
    print(f"  Δchain_purity(+causal - semantic): {delta_chain:+.3f} (需 ≥ +0.10)")
    print(f"  Δevent_purity(+causal - semantic): {delta_event:+.3f} (需 ≥ -0.10)")
    print(f"  判定: {h003}")

    ts = time.strftime("%Y%m%d-%H%M%S")
    default_out = Path(__file__).resolve().parents[1] / "research" / "results"
    out = Path(args.out) if args.out else default_out
    out.mkdir(parents=True, exist_ok=True)
    out_path = out / f"EXP-002-h003-{ts}.json"
    out_path.write_text(
        json.dumps({
            "meta": {"experiment": "EXP-002-h003", "timestamp": ts,
                     "corpus": CORPUS_CFG,
                     "judgement_threshold": JUDGEMENT_THRESHOLD,
                     "full_layer_thresholds": FULL_LAYER_THRESHOLDS},
            "corpus_stats": stats,
            "full_layer": full,
            "retrieval_layer": per_strategy,
            "judgement": {"H-003": h003, "delta_chain_purity": round(delta_chain, 4),
                          "delta_event_purity": round(delta_event, 4)},
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n原始数据: {out_path}")


def _GRAPH_MODE_KW(mode: str) -> dict[str, Any]:
    for m, kw in GRAPH_MODES:
        if m == mode:
            return kw
    raise KeyError(mode)


if __name__ == "__main__":
    main()
