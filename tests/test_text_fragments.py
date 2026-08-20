"""E0.5 文本碎片语料: 结构族对齐 / 确定性 / 文本分层 / 查询语义 / 黄金哈希。"""
from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import fields
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO / "src") not in sys.path:
    sys.path.insert(0, str(REPO / "src"))

from cognitive_os.datasets.synthetic_events import (  # noqa: E402
    SyntheticCorpusConfig,
)
from cognitive_os.datasets.text_fragments import (  # noqa: E402
    ENTITY_LEXICON,
    NOISE_LEXICON,
    TextFragmentConfig,
    TextFragmentCorpus,
)


def _default():
    return TextFragmentCorpus(TextFragmentConfig())


def test_structure_counts():
    c = _default()
    assert len(c.points) == 96
    assert len(c.events) == 12
    assert all(len(v) == 8 for v in c.events.values())
    assert len({p.source for p in c.points}) == 4
    assert all(p.source_weight >= 0.6 for p in c.points)
    assert all(0.0 <= p.timestamp <= 100.0 for p in c.points)
    for ev, pids in c.events.items():
        start = c.event_start(ev)
        assert all(start <= c.get(p).timestamp <= start + 20.0 for p in pids)


def test_config_parity_with_synthetic():
    a = {f.name for f in fields(TextFragmentConfig)}
    b = {f.name for f in fields(SyntheticCorpusConfig)}
    assert a == b - {"embed_dim", "index_top_m"}


def test_determinism():
    c1 = _default()
    c2 = _default()
    assert [p.text for p in c1.points] == [p.text for p in c2.points]
    assert [(p.pid, p.source, p.timestamp) for p in c1.points] == [
        (p.pid, p.source, p.timestamp) for p in c2.points
    ]
    c3 = TextFragmentCorpus(TextFragmentConfig(seed=7))
    assert [p.text for p in c3.points] != [p.text for p in c1.points]


def test_text_layers():
    c = _default()
    for p in c.points:
        assert p.text
        assert p.embedding == ()
        assert any(t in p.text for t in c.topics)
        assert any(ent in p.text for ent in ENTITY_LEXICON)
    c0 = TextFragmentCorpus(TextFragmentConfig(within_event_noise=0.0))
    assert not any(w in p.text for p in c0.points for w in NOISE_LEXICON)
    c1 = TextFragmentCorpus(TextFragmentConfig(within_event_noise=1.0))
    assert all(any(w in p.text for w in NOISE_LEXICON) for p in c1.points)


def test_causal_mentions():
    c = TextFragmentCorpus(TextFragmentConfig(causal_chains=2))
    n_with = sum(1 for p in c.points if p.meta.get("mentions"))
    assert n_with > 0
    pid_set = set(c.point_ids)
    for p in c.points:
        if "mentions" in p.meta:
            assert c.chain_of(p.pid) >= 0
            for ref in p.meta["mentions"]:
                assert ref in pid_set
                assert ref in p.text
    assert any(c.chain_of(p.pid) >= 0 for p in c.points)


def test_queries_mirror_semantics():
    c = _default()
    qs = c.sample_queries(6, rng_seed=3)
    assert [q.qid for q in qs] == [f"q{i:03d}" for i in range(6)]
    for q in qs:
        assert q.seed_pids[0] in c.events[q.event_id]
        assert q.allowed_pids is None
    qs2 = c.sample_queries(6, rng_seed=3)
    assert [(q.qid, q.seed_pids, q.event_id) for q in qs] == [
        (q.qid, q.seed_pids, q.event_id) for q in qs2
    ]
    qt = c.sample_queries(6, rng_seed=3, truncate_frac=0.6)
    for q in qt:
        assert q.allowed_pids is not None
        t_obs = c.event_start(q.event_id) + 0.6 * 20.0
        assert c.get(q.seed_pids[0]).timestamp <= t_obs
        assert set(q.allowed_pids) == set(c.observable_pids(t_obs))


def test_future_fragments_and_observable():
    c = _default()
    ev = sorted(c.events)[0]
    start = c.event_start(ev)
    mid = start + 0.5 * 20.0
    fut = c.future_fragments(ev, mid)
    assert all(c.get(p).timestamp > mid for p in fut)
    obs = set(c.observable_pids(mid))
    assert set(fut).isdisjoint(obs)


def test_golden_structure():
    c = _default()
    lines = []
    for p in c.points:
        meta = json.dumps(p.meta, ensure_ascii=False, sort_keys=True)
        lines.append(
            f"{p.pid}|{p.event_id}|{p.source}|{p.source_weight:.4f}|{p.timestamp:.4f}|{meta}|{p.text}"
        )
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    assert digest == "13f349142076d2967d842fd34baea26b102a70bc88bea98270c73a64f661dbec"
