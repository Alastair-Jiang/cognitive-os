"""EXP-004a 运行器测试: 语料宇宙 / 工厂零漂移 / 效用 / 聚合 / G1 判定。"""
from __future__ import annotations

import sys
from math import isclose
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for p in (REPO / "src", REPO / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from cognitive_os.datasets.synthetic_events import SyntheticCorpusConfig  # noqa: E402
from run_exp002_scan import NOISE_LEVELS, OVERLAP_LEVELS, grid_corpus_config  # noqa: E402
import run_exp004a_oracle as r4a  # noqa: E402


def test_corpus_universe_ten_configs():
    cells = r4a.corpus_universe()
    assert len(cells) == 10
    labels = [c["cell"] for c in cells]
    assert len(set(labels)) == 10
    assert labels[-1] == "medium"
    assert labels[0] == "overlap-low-noise-low"


def test_medium_params_match_frozen_config():
    m = r4a.medium_corpus_params()
    assert m["n_events"] == 30
    assert m["fragments_per_event"] == 10
    assert m["n_topics"] == 6
    assert m["topics_per_event"] == 4
    assert m["within_event_noise"] == 0.45
    assert "seed" not in m
    med = r4a.corpus_universe()[-1]
    assert med["corpus_cfg"].n_events == 30
    assert med["corpus_cfg"].embed_dim == 32


def test_grid_levels_imported_not_copied():
    assert r4a.OVERLAP_LEVELS is OVERLAP_LEVELS
    assert r4a.NOISE_LEVELS is NOISE_LEVELS
    assert len(r4a.OVERLAP_LEVELS) * len(r4a.NOISE_LEVELS) == 9


def test_grid_corpus_config_parity():
    cfg = grid_corpus_config(4, 0.30, 20260819)
    expect = SyntheticCorpusConfig(
        n_events=12,
        fragments_per_event=8,
        embed_dim=24,
        n_topics=5,
        topics_per_event=4,
        within_event_noise=0.30,
        time_horizon=100.0,
        event_span=20.0,
        source_count=4,
        source_min_weight=0.6,
        primary_source_prob=0.6,
        index_top_m=6,
        seed=20260819,
    )
    assert cfg == expect


def test_frozen_constants():
    assert r4a.SEEDS_DEFAULT == [20260819, 7, 42]
    assert r4a.SEEDS_BOUNDARY_EXT == [131, 9999]
    assert r4a.LAMBDA_MAIN == 0.02
    assert r4a.LAMBDA_SWEEP == [0.0, 0.01, 0.02, 0.05, 0.1]
    assert r4a.LAMBDA_MAIN in r4a.LAMBDA_SWEEP
    assert (r4a.N_QUERIES, r4a.QUERY_SEED, r4a.K) == (12, 1, 10)
    assert r4a.G1_H1_POOLED_MIN == 0.03
    assert r4a.G1_H1_CELL_MIN == 0.02
    assert r4a.G1_MIN_CELLS == 3


def test_utility_formula():
    assert isclose(r4a.utility(0.8, 100, 100, 0.02), 0.78, abs_tol=1e-12)
    assert isclose(r4a.utility(0.9, 1400, 100, 0.02), 0.62, abs_tol=1e-12)
    assert isclose(r4a.utility(0.9, 1400, 100, 0.0), 0.9, abs_tol=1e-12)


def _mk_run(n_points, rows):
    pq = {}
    for i, (fa, ca, fb, cb, fc, cc) in enumerate(rows):
        pq[f"q{i:03d}"] = {
            "event_id": "e",
            "seed": ["p"],
            "strategies": {
                "A-traditional": {"f1_at_k": fa, "similarity_calls": ca, "u_main": 0.0},
                "B-anchor": {"f1_at_k": fb, "similarity_calls": cb, "u_main": 0.0},
                "C-multinet": {"f1_at_k": fc, "similarity_calls": cc, "u_main": 0.0},
            },
        }
    return {"corpus_seed": 1, "n_points": n_points, "per_query": pq}


def test_aggregate_formulas():
    lam = 0.02
    cells = {
        "c1": [_mk_run(100, [(0.8, 100, 0.7, 20, 0.9, 1400), (0.6, 100, 0.5, 20, 0.4, 1400)])],
        "c2": [_mk_run(200, [(0.5, 200, 0.9, 40, 0.2, 2800)])],
        "c3": [_mk_run(100, [(0.9, 100, 0.5, 20, 0.1, 1400), (0.5, 100, 0.9, 20, 0.1, 1400)])],
    }
    agg = r4a.aggregate_lambda(cells, lam)
    assert agg["u_gf_strategy"] == "B-anchor"
    assert isclose(agg["u_gf"], 0.696, abs_tol=1e-12)
    c1 = agg["cells"]["c1"]
    assert c1["best_fixed"] == "A-traditional"
    assert isclose(c1["u_cf"], 0.68, abs_tol=1e-12)
    assert isclose(c1["h1"], 0.0, abs_tol=1e-12)
    c2 = agg["cells"]["c2"]
    assert isclose(c2["u_cf"], 0.896, abs_tol=1e-12)
    assert isclose(c2["h1"], 0.0, abs_tol=1e-12)
    c3 = agg["cells"]["c3"]
    assert isclose(c3["u_cf"], 0.696, abs_tol=1e-12)
    assert isclose(c3["u_or"], 0.888, abs_tol=1e-12)
    assert isclose(c3["h1"], 0.192, abs_tol=1e-12)
    assert isclose(agg["h0_pooled"], ((0.68 - 0.696) + (0.896 - 0.696) + 0.0) / 3, abs_tol=1e-12)
    assert isclose(agg["h1_pooled"], 0.192 / 3, abs_tol=1e-12)


def test_decide_branches():
    cells_ok = {f"c{i}": {"h1": 0.05} for i in range(10)}
    cells_no = {f"c{i}": {"h1": 0.0} for i in range(10)}
    cells_two = dict(cells_no)
    cells_two["c0"] = {"h1": 0.05}
    cells_two["c1"] = {"h1": 0.05}

    def agg(h1, h0, cells):
        return {"h1_pooled": h1, "h0_pooled": h0, "cells": cells}

    assert r4a.decide(agg(0.05, 0.10, cells_ok))["verdict"] == "PASS"
    assert r4a.decide(agg(0.01, 0.05, cells_no))["verdict"] == "REGIME"
    assert r4a.decide(agg(0.01, 0.01, cells_no))["verdict"] == "FAIL"
    d = r4a.decide(agg(0.05, 0.01, cells_two))
    assert d["verdict"] == "EDGE"
    assert d["boundary_flag"] is True
    assert d["cells_with_h1_ge_0.02"] == 2


def test_run_cell_seed_records():
    cell = {
        "cell": "tiny",
        "corpus_cfg": SyntheticCorpusConfig(
            n_events=4,
            fragments_per_event=4,
            embed_dim=16,
            n_topics=3,
            topics_per_event=2,
            within_event_noise=0.3,
            time_horizon=100.0,
            event_span=20.0,
            source_count=3,
            source_min_weight=0.6,
            primary_source_prob=0.6,
            index_top_m=4,
            seed=7,
        ),
        "params": {},
    }
    run = r4a.run_cell_seed(cell, 7, nq=4, k=6)
    assert run["n_points"] == 16
    assert len(run["per_query"]) == 4
    for q in run["per_query"].values():
        assert set(q["strategies"]) == set(r4a.EXPECTED_STRATEGIES)
        for s, rec in q["strategies"].items():
            assert 0.0 <= rec["f1_at_k"] <= 1.0
            assert rec["similarity_calls"] >= 0
            assert isclose(
                rec["u_main"],
                r4a.utility(
                    rec["f1_at_k"], rec["similarity_calls"], run["n_points"], r4a.LAMBDA_MAIN
                ),
                abs_tol=1e-12,
            )
    agg = r4a.aggregate_lambda({"tiny": [run]}, r4a.LAMBDA_MAIN)
    assert isclose(agg["u_gf"], max(agg["pooled_mean_u"].values()), abs_tol=1e-12)
    assert set(agg["cells"]["tiny"]) >= {"u_cf", "best_fixed", "u_or", "h0", "h1"}
