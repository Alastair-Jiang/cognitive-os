"""相似度函数(纯标准库实现)。"""

from __future__ import annotations

from typing import Sequence, Tuple

Vector = Sequence[float]


def dot(a: Vector, b: Vector) -> float:
    return sum(x * y for x, y in zip(a, b))


def norm(a: Vector) -> float:
    return dot(a, a) ** 0.5


def cosine(a: Vector, b: Vector) -> float:
    """余弦相似度, 落在 [-1, 1]; 零向量返回 0.0。"""
    na, nb = norm(a), norm(b)
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot(a, b) / (na * nb)


def l2(a: Vector, b: Vector) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5


def add(a: Vector, b: Vector) -> Tuple[float, ...]:
    return tuple(x + y for x, y in zip(a, b))


def scale(v: Vector, s: float) -> Tuple[float, ...]:
    return tuple(x * s for x in v)


def normalize(v: Vector) -> Tuple[float, ...]:
    n = norm(v)
    if n == 0.0:
        return tuple(v)
    return tuple(x / n for x in v)


def mean_embedding(vectors: Sequence[Vector]) -> Tuple[float, ...]:
    """多个向量的均值并归一化(种子碎片查询表示)。"""
    if not vectors:
        return ()
    dim = len(vectors[0])
    acc = [0.0] * dim
    for v in vectors:
        for i, x in enumerate(v):
            acc[i] += x
    return normalize(tuple(x / len(vectors) for x in acc))
