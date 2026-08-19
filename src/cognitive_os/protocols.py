"""三协议(ADR-0001): 语料 / 嵌入器 / 索引的最小策略面。

原则:
1. 策略栈(retrieval / nets / anchors / validation)只依赖本模块,
   不得引入具体语料实现(ADR-0001 验收条件, 由单测机器验证);
2. 结构化鸭子类型: SyntheticEventCorpus 天然满足 Corpus 协议;
3. 纯标准库(ADR-0002 零依赖红线不动); GPU 实现走可选 extras(ADR-0003)。
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from .types import Embedding, InformationPoint


@runtime_checkable
class Embedder(Protocol):
    """嵌入协议: 种子碎片序列映射为查询表示向量。

    恒等实现直接取点上的预计算向量; GPU 实现(EXP-006)把种子文本
    送入真嵌入模型再取均值。差异对策略栈不可见。
    """

    def seed_vec(self, seed_points: Sequence[InformationPoint]) -> Embedding: ...


@runtime_checkable
class Index(Protocol):
    """索引协议: pid 到 [(邻居 pid, 余弦相似度)] 的降序表。

    暴力实现预计算邻居表; ANN 实现(EXP-007)允许召回损失,
    但与暴力真值的偏差必须单独度量。
    """

    def neighbors(self, pid: str, k: int | None = None) -> list[tuple[str, float]]: ...


@runtime_checkable
class Corpus(Protocol):
    """语料协议: 检索策略可依赖的最小语料面(策略栈唯一入口)。"""

    @property
    def point_ids(self) -> list[str]: ...

    def get(self, pid: str) -> InformationPoint: ...

    def embed_seed(self, seed_pids: Sequence[str]) -> Embedding: ...

    def neighbors(self, pid: str, k: int | None = None) -> list[tuple[str, float]]: ...
