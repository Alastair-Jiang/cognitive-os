"""三协议与恒等适配器: 结构一致性 + 逐成员对账(E1)。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for _p in (str(REPO / "src"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from cognitive_os.adapters.identity import identity_view  # noqa: E402
from cognitive_os.datasets.synthetic_events import (  # noqa: E402
    SyntheticCorpusConfig,
    SyntheticEventCorpus,
)
from cognitive_os.protocols import Corpus, Embedder, Index  # noqa: E402
import run_benchmark  # noqa: E402


def _corpora():
    cfg = SyntheticCorpusConfig(
        n_events=6,
        fragments_per_event=5,
        embed_dim=12,
        causal_chains=2,
    )
    corpus = SyntheticEventCorpus(cfg)
    view = identity_view(corpus.points, cfg.index_top_m)
    return corpus, view


def _s_cfg():
    cfg_path = REPO / "configs" / "benchmark.small.json"
    return json.loads(cfg_path.read_text(encoding="utf-8"))["strategies"]


def test_structural_conformance():
    corpus, view = _corpora()
    assert isinstance(corpus, Corpus)
    assert isinstance(view, Corpus)
    assert isinstance(view.embedder, Embedder)
    assert isinstance(view.index, Index)


def test_point_store_identity():
    corpus, view = _corpora()
    assert view.point_ids == corpus.point_ids
    for pid in corpus.point_ids:
        assert view.get(pid) == corpus.get(pid)
        assert view.event_of(pid) == corpus.event_of(pid)
        assert view.mentions(pid) == corpus.mentions(pid)
    for ev in sorted(corpus.events):
        assert view.event_fragments(ev) == corpus.event_fragments(ev)


def test_embed_seed_matches():
    corpus, view = _corpora()
    for q in corpus.sample_queries(5, rng_seed=3):
        assert view.embed_seed(q.seed_pids) == corpus.embed_seed(q.seed_pids)


def test_neighbors_match():
    corpus, view = _corpora()
    for pid in corpus.point_ids:
        assert view.neighbors(pid) == corpus.neighbors(pid)
    pid0 = corpus.point_ids[0]
    assert view.neighbors(pid0, k=3) == corpus.neighbors(pid0, k=3)


def test_strategies_identical_across_paths():
    corpus, view = _corpora()
    queries = corpus.sample_queries(6, rng_seed=5)
    direct = run_benchmark.build_strategies(corpus, _s_cfg())
    via_view = run_benchmark.build_strategies(view, _s_cfg())
    for s1, s2 in zip(direct, via_view):
        assert s1.name == s2.name
        for q in queries:
            r1 = s1.retrieve(q, 5)
            r2 = s2.retrieve(q, 5)
            assert r1.ranked_pids == r2.ranked_pids
            assert r1.scores == r2.scores
            assert r1.similarity_calls == r2.similarity_calls
            assert r1.index_lookups == r2.index_lookups
            assert r1.iterations == r2.iterations
            assert r1.early_stopped == r2.early_stopped
            assert set(r1.evidence) == set(r2.evidence)
            for pid in r1.evidence:
                assert r1.evidence[pid] == r2.evidence[pid]


def test_runner_build_strategies_accepts_view():
    corpus, view = _corpora()
    strategies = run_benchmark.build_strategies(view, _s_cfg())
    q = corpus.sample_queries(1, rng_seed=2)[0]
    for s in strategies:
        res = s.retrieve(q, 5)
        assert res.ranked_pids
