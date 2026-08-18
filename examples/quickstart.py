"""快速示例: 合成语料 + 三策略 + 一次查询的对比。

运行:
    python examples/quickstart.py
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cognitive_os.anchors.anchor_detector import AnchorConfig
from cognitive_os.datasets.synthetic_events import SyntheticEventCorpus
from cognitive_os.nets.search_net import SearchNetConfig
from cognitive_os.retrieval.strategy_a_traditional import TraditionalRetrieval
from cognitive_os.retrieval.strategy_b_anchor import AnchorRetrieval
from cognitive_os.retrieval.strategy_c_multinet import DynamicMultiNetRetrieval
from cognitive_os.validation.progressive import ValidatorConfig


def main() -> None:
    corpus = SyntheticEventCorpus()
    stats = corpus.similarity_stats()
    print(f"语料: {len(corpus.points)} 个碎片, {len(corpus.events)} 个事件")
    print(f"同事件平均相似度={stats['within_mean']:.3f}, "
          f"跨事件平均={stats['cross_mean']:.3f}, "
          f"跨事件最大={stats['cross_max']:.3f} (存在歧义: {stats['cross_max'] > stats['within_mean'] * 0.6})")

    query = corpus.sample_queries(1, rng_seed=7)[0]
    print(f"\n查询 qid={query.qid} 种子={query.seed_pids[0]} 目标事件={query.event_id}")
    k = 10

    a = TraditionalRetrieval(corpus, source_bonus=0.05)
    b = AnchorRetrieval(
        corpus,
        anchor_cfg=AnchorConfig(n_anchors=3),
        net_cfg=SearchNetConfig(name="B-expansion", radius=0.72, temporal_window=40.0, max_hops=1),
    )
    c = DynamicMultiNetRetrieval(
        corpus,
        net_configs=[
            SearchNetConfig(name="narrow-semantic", radius=0.88, semantic_w=1.0, max_hops=1),
            SearchNetConfig(name="wide-source", radius=0.7, source_w=0.4, semantic_w=0.5, temporal_window=40.0),
        ],
        validator_cfg=ValidatorConfig(),
    )

    relevant = set(corpus.event_fragments(query.event_id)) - set(query.seed_pids)
    for strat in (a, b, c):
        res = strat.retrieve(query, k)
        hits = [pid for pid in res.ranked_pids if pid in relevant]
        print(f"\n[{strat.name}] iterations={res.iterations} sim_calls={res.similarity_calls} "
              f"idx_lookups={res.index_lookups} latency={res.latency_ms:.2f}ms early_stop={res.early_stopped}")
        print(f"  top-{k} 命中目标事件 {len(hits)}/{len(relevant)}: {hits[:5]}")


if __name__ == "__main__":
    main()
