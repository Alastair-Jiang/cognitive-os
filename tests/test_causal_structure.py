"""H-003 重设计新增功能的单元测试: 因果链语料 / 引用边 / 共识聚合。"""

from __future__ import annotations

from cognitive_os.datasets.synthetic_events import SyntheticCorpusConfig, SyntheticEventCorpus
from cognitive_os.graph.evidence_graph import EvidenceGraph
from cognitive_os.metrics import chain_purity, mean_chain_purity, mean_component_purity
from cognitive_os.types import Evidence
from cognitive_os.validation.progressive import ProgressiveValidator, ValidatorConfig


def make_corpus(**overrides):
    cfg = SyntheticCorpusConfig(
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
        **overrides,
    )
    return SyntheticEventCorpus(cfg)


def test_causal_chains_default_off():
    """causal_chains=0(默认) 时行为与旧版完全一致: 无 chain_id / mentions。"""
    corpus = SyntheticEventCorpus(SyntheticCorpusConfig())
    assert all(corpus.chain_of(p) == -1 for p in corpus.point_ids)
    assert all(corpus.mentions(p) == [] for p in corpus.point_ids)


def test_chain_ids_assigned():
    corpus = make_corpus()
    chain_ids = {corpus.chain_of(p) for p in corpus.point_ids}
    assert chain_ids == {0, 1, 2}


def test_mentions_only_point_to_next_event_in_chain():
    corpus = make_corpus()
    for p in corpus.point_ids:
        for target in corpus.mentions(p):
            # 引用目标必须是链内下一事件(不是自己、不是其他链)
            assert corpus.event_of(target) != corpus.event_of(p)
            assert corpus.chain_of(target) == corpus.chain_of(p)


def test_mentions_some_fragments_have_refs():
    corpus = make_corpus()
    mentioned = sum(1 for p in corpus.point_ids if corpus.mentions(p))
    assert mentioned > 0  # mention_prob=0.4 × 96 碎片, 必有引用


def test_reference_edge_built_with_causal_edges():
    corpus = make_corpus()
    # 找一个有 mentions 的碎片
    src = next(p for p in corpus.point_ids if corpus.mentions(p))
    target = corpus.mentions(src)[0]
    g = EvidenceGraph.build(corpus, [src, target], semantic_threshold=0.99)
    assert not g.has_edge(src, target)  # 语义阈值远高于 → 无语义边
    g2 = EvidenceGraph.build(corpus, [src, target], semantic_threshold=0.99, causal_edges=True)
    assert g2.has_edge(src, target)  # 引用边不依赖语义阈值


def test_reference_edge_ignored_without_causal_edges():
    corpus = make_corpus()
    src = next(p for p in corpus.point_ids if corpus.mentions(p))
    target = corpus.mentions(src)[0]
    g = EvidenceGraph.build(corpus, [src, target], causal_edges=False)
    assert not g.has_edge(src, target)


def test_mean_component_purity_weights_by_size():
    pid_to_event = {"a": "e1", "b": "e1", "c": "e2", "d": "e3"}
    # 成分1: {a,b} 纯度 1.0; 成分2: {c} 纯度 1.0; 成分3: {d} 纯度 1.0 → 1.0
    comps = [["a", "b"], ["c"], ["d"]]
    assert mean_component_purity(comps, pid_to_event) == 1.0
    # 一个不纯成分: {a, c} → 0.5, 大小 2, 整体 = (2×0.5 + 1) / 3 = 0.667
    comps2 = [["a", "c"], ["d"]]
    assert abs(mean_component_purity(comps2, pid_to_event) - 0.6667) < 1e-3


def test_chain_purity():
    pid_to_chain = {"a": 0, "b": 0, "c": 1, "d": -1}
    assert chain_purity(["a", "b", "c"], pid_to_chain) == 2 / 3
    assert abs(mean_chain_purity([["a", "b", "c"], ["d"]], pid_to_chain) - 0.75) < 1e-9


def test_validator_aggregation_mean():
    v = ProgressiveValidator(ValidatorConfig(aggregation="mean"))
    v.add_round([Evidence(pid="p1", score=0.9)], "net1")
    v.add_round([Evidence(pid="p1", score=0.5)], "net2")
    v.update_confidence()
    assert abs(v.evidence["p1"].score - 0.7) < 1e-9


def test_validator_aggregation_max_default():
    v = ProgressiveValidator()
    v.add_round([Evidence(pid="p1", score=0.9)], "net1")
    v.add_round([Evidence(pid="p1", score=0.5)], "net2")
    v.update_confidence()
    assert abs(v.evidence["p1"].score - 0.9) < 1e-9


def test_validator_rejects_unknown_aggregation():
    import pytest

    with pytest.raises(ValueError):
        ProgressiveValidator(ValidatorConfig(aggregation="median"))
