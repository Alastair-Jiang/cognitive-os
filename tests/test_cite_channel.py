"""E2 前置: 引用扩张通道 + 有序路径恢复率黄金值。"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for p in (str(REPO / "src"), str(REPO / "scripts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from cognitive_os.datasets.synthetic_events import (  # noqa: E402
    SyntheticCorpusConfig,
    SyntheticEventCorpus,
)
from cognitive_os.metrics import ordered_path_recovery  # noqa: E402
from cognitive_os.nets.search_net import (  # noqa: E402
    NetSearchStats,
    SearchNet,
    SearchNetConfig,
)
from cognitive_os.protocols import Corpus  # noqa: E402


def _event_of(mapping):
    def fn(pid):
        return mapping[pid]

    return fn


def _mentions_of(mapping):
    def fn(pid):
        return list(mapping.get(pid, []))

    return fn


CHAIN = ["e1", "e2", "e3", "e4"]
EV_OF = _event_of({"e1f": "e1", "e2f": "e2", "e3f": "e3", "e4f": "e4"})
FULL_MENTIONS = _mentions_of({"e1f": ["e2f"], "e2f": ["e3f"], "e3f": ["e4f"]})


def test_ordered_path_recovery_golden():
    assert ordered_path_recovery(["e1f", "e2f", "e3f"], [CHAIN], EV_OF, FULL_MENTIONS) == 0.75
    assert ordered_path_recovery(["e1f", "e3f"], [CHAIN], EV_OF, FULL_MENTIONS) == 0.25
    assert ordered_path_recovery(["e3f", "e4f"], [CHAIN], EV_OF, FULL_MENTIONS) == 0.5
    assert ordered_path_recovery([], [CHAIN], EV_OF, FULL_MENTIONS) == 0.0
    m2 = _mentions_of({"e1f": ["e2f"]})
    assert ordered_path_recovery(["e1f", "e2f", "e3f", "e4f"], [CHAIN], EV_OF, m2) == 0.5


def test_ordered_path_recovery_mean():
    full = ordered_path_recovery(["e1f", "e2f", "e3f", "e4f"], [CHAIN, CHAIN], EV_OF, FULL_MENTIONS)
    assert full == 1.0
    part = ordered_path_recovery(["e1f", "e3f"], [CHAIN, CHAIN], EV_OF, FULL_MENTIONS)
    assert part == 0.25


def _causal_corpus():
    cfg = SyntheticCorpusConfig(
        n_events=6,
        fragments_per_event=3,
        embed_dim=12,
        n_topics=4,
        topics_per_event=2,
        within_event_noise=0.2,
        causal_chains=2,
        mention_prob=1.0,
        index_top_m=6,
        seed=7,
    )
    return SyntheticEventCorpus(cfg)


def test_protocol_mentions_conformance():
    corpus = _causal_corpus()
    assert isinstance(corpus, Corpus)
    assert callable(corpus.mentions)


def _pid_with_mentions(corpus):
    for pid in corpus.point_ids:
        if corpus.mentions(pid):
            return pid
    return None


def test_cite_expansion_pulls_below_radius():
    corpus = _causal_corpus()
    seed = [_pid_with_mentions(corpus)]
    assert seed[0] is not None
    cited = set(corpus.mentions(seed[0]))
    cfg = SearchNetConfig(radius=0.999, max_hops=1, max_candidates_per_anchor=50, cite_expansion=True)
    net = SearchNet(corpus, cfg)
    evs = net.search(seed)
    got = set(e.pid for e in evs)
    assert cited & got


def test_cite_expansion_bills_index_lookups():
    corpus = _causal_corpus()
    seed = [_pid_with_mentions(corpus)]
    cfg_off = SearchNetConfig(radius=0.7, max_hops=1, cite_expansion=False)
    cfg_on = SearchNetConfig(radius=0.7, max_hops=1, cite_expansion=True)
    s_off = NetSearchStats()
    s_on = NetSearchStats()
    SearchNet(corpus, cfg_off).search(seed, stats=s_off)
    SearchNet(corpus, cfg_on).search(seed, stats=s_on)
    assert s_on.index_lookups > s_off.index_lookups
    assert s_on.similarity_calls >= s_off.similarity_calls
