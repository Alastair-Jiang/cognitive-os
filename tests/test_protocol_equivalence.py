"""E1 行为等价(测试门禁版): 视图路径与直接路径逐字段一致。"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
for _p in (str(REPO / "src"), str(REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import prove_protocol_equivalence as proof  # noqa: E402


def test_small_config_full_equivalence():
    result = proof.run_comparison(
        config=str(REPO / "configs" / "benchmark.small.json"),
        queries=12,
        k=10,
        query_seed=1,
        truncate_frac=None,
    )
    assert result["diffs"] == []
    assert result["verdict"] == "PASS"


def test_small_config_truncated_equivalence():
    result = proof.run_comparison(
        config=str(REPO / "configs" / "benchmark.small.json"),
        queries=12,
        k=10,
        query_seed=1,
        truncate_frac=0.6,
    )
    assert result["diffs"] == []
    assert result["verdict"] == "PASS"
