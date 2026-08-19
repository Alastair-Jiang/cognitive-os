"""ADR-0001 验收条件机器验证: 策略栈不得引入具体语料实现。

扫描范围: retrieval / nets / anchors / validation 四个策略栈目录;
证据图(graph)属事后评估层, 允许依赖具体语料(超出本验收范围)。
"""
from __future__ import annotations

from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src" / "cognitive_os"
STACK_DIRS = ("retrieval", "nets", "anchors", "validation")
FORBIDDEN = (
    "datasets",
    "SyntheticEventCorpus",
)


def test_strategy_stack_is_pure():
    checked = 0
    for sub in STACK_DIRS:
        files = sorted((SRC / sub).glob("*.py"))
        assert files, f"目录缺失: {sub}"
        for py in files:
            src = py.read_text(encoding="utf-8")
            for pat in FORBIDDEN:
                assert pat not in src, f"{py.name} 违反 ADR-0001: 出现 {pat}"
            checked += 1
    assert checked >= 7
