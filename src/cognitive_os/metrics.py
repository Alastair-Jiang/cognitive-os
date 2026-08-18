"""检索与结构重建指标(纯标准库)。"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Sequence, Set


def precision_at_k(ranked: Sequence[str], relevant: Set[str], k: int) -> float:
    top = ranked[:k]
    if not top:
        return 0.0
    return sum(1 for pid in top if pid in relevant) / len(top)


def recall_at_k(ranked: Sequence[str], relevant: Set[str], k: int) -> float:
    if not relevant:
        return 0.0
    top = ranked[:k]
    return sum(1 for pid in top if pid in relevant) / len(relevant)


def f1_at_k(precision: float, recall: float) -> float:
    if precision + recall == 0.0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def _dcg(rewards: Sequence[float]) -> float:
    return sum(r / math.log2(i + 2) for i, r in enumerate(rewards))


def ndcg_at_k(ranked: Sequence[str], relevant: Set[str], k: int) -> float:
    """二值相关性下的 NDCG@k。"""
    top = ranked[:k]
    if not top:
        return 0.0
    rewards = [1.0 if pid in relevant else 0.0 for pid in top]
    dcg = _dcg(rewards)
    ideal = [1.0] * min(k, len(relevant))
    idcg = _dcg(ideal)
    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def mrr(ranked: Sequence[str], relevant: Set[str]) -> float:
    """第一个相关点的倒数排名; 无相关点返回 0。"""
    for i, pid in enumerate(ranked):
        if pid in relevant:
            return 1.0 / (i + 1)
    return 0.0


def jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# ---------------------------------------------------------------------------
# 结构重建指标(H-003 / RQ-4)
# ---------------------------------------------------------------------------


def cluster_purity(component_pids: Sequence[str], pid_to_event: Dict[str, str]) -> float:
    """连通成分的纯度: 最大事件占比。

    纯度为 1.0 表示成分完全由单一事件构成。
    """
    if not component_pids:
        return 0.0
    counts: Dict[str, int] = {}
    for pid in component_pids:
        ev = pid_to_event.get(pid, "")
        counts[ev] = counts.get(ev, 0) + 1
    return max(counts.values()) / len(component_pids)


def mean_component_purity(
    components: Sequence[Sequence[str]], pid_to_event: Dict[str, str]
) -> float:
    """聚类级纯度(H-003 重设计): 全部连通成分纯度的按大小加权平均。

    只测种子成分会遗漏“其他成分是否被正确拆分”; 加权平均给出
    整张图的结构质量。孤立点成分(大小 1)纯度为 1.0。
    """
    total = sum(len(c) for c in components)
    if total == 0:
        return 0.0
    return sum(len(c) * cluster_purity(c, pid_to_event) for c in components) / total


def chain_purity(component_pids: Sequence[str], pid_to_chain: Dict[str, int]) -> float:
    """成分的链纯度: 最大因果链占比(测“结构信号把链聚起来”)。

    与 cluster_purity 的唯一区别是 ground-truth 标签为链而非事件。
    """
    if not component_pids:
        return 0.0
    counts: Dict[int, int] = {}
    for pid in component_pids:
        ch = pid_to_chain.get(pid, -1)
        counts[ch] = counts.get(ch, 0) + 1
    return max(counts.values()) / len(component_pids)


def mean_chain_purity(
    components: Sequence[Sequence[str]], pid_to_chain: Dict[str, int]
) -> float:
    """聚类级链纯度: 全部成分的链纯度按大小加权平均。"""
    total = sum(len(c) for c in components)
    if total == 0:
        return 0.0
    return sum(len(c) * chain_purity(c, pid_to_chain) for c in components) / total


def reconstruction_metrics(
    component_pids: Sequence[str], true_event_pids: Set[str]
) -> Dict[str, float]:
    """以 ground-truth 事件为参照, 度量成分的重建质量。"""
    if not component_pids:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    component = set(component_pids)
    prec = len(component & true_event_pids) / len(component) if component else 0.0
    rec = len(component & true_event_pids) / len(true_event_pids) if true_event_pids else 0.0
    f1 = f1_at_k(prec, rec)
    return {"precision": prec, "recall": rec, "f1": f1}


def rank_stats(ranked: Sequence[str], relevant: Set[str], k: int) -> Dict[str, float]:
    """一次检索的完整指标快照。"""
    p = precision_at_k(ranked, relevant, k)
    r = recall_at_k(ranked, relevant, k)
    return {
        "precision_at_k": p,
        "recall_at_k": r,
        "f1_at_k": f1_at_k(p, r),
        "ndcg_at_k": ndcg_at_k(ranked, relevant, k),
        "mrr": mrr(ranked, relevant),
    }
