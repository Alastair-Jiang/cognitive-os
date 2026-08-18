"""检索策略接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..datasets.synthetic_events import SyntheticEventCorpus
from ..types import Query, RetrievalResult


class RetrievalStrategy(ABC):
    """检索策略抽象基类。

    所有策略必须诚实记录效率计数(similarity_calls / index_lookups /
    iterations / latency_ms), 见 system_constitution.md 第 3 条。
    """

    name: str = "base"

    def __init__(self, corpus: SyntheticEventCorpus):
        self.corpus = corpus

    @abstractmethod
    def retrieve(self, query: Query, k: int) -> RetrievalResult:
        """对单个查询执行检索, 返回排序结果与效率计数。"""
