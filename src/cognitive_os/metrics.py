"""检索与结构重建指标(纯标准库)。"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence


def precision_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
    top = ranked[:k]
    if not top:
        return 0.0
    return sum(1 for pid in top if pid in relevant) / len(top)


def recall_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
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


def ndcg_at_k(ranked: Sequence[str], relevant: set[str], k: int) -> float:
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


def mrr(ranked: Sequence[str], relevant: set[str]) -> float:
    """第一个相关点的倒数排名; 无相关点返回 0。"""
    for i, pid in enumerate(ranked):
        if pid in relevant:
            return 1.0 / (i + 1)
    return 0.0


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def mean(values: Sequence[float]) -> float:
    return sum(values) / len(values) if values else 0.0


# ---------------------------------------------------------------------------
# 结构重建指标(H-003 / RQ-4)
# ---------------------------------------------------------------------------


def cluster_purity(component_pids: Sequence[str], pid_to_event: dict[str, str]) -> float:
    """连通成分的纯度: 最大事件占比。

    纯度为 1.0 表示成分完全由单一事件构成。
    """
    if not component_pids:
        return 0.0
    counts: dict[str, int] = {}
    for pid in component_pids:
        ev = pid_to_event.get(pid, "")
        counts[ev] = counts.get(ev, 0) + 1
    return max(counts.values()) / len(component_pids)


def mean_component_purity(
    components: Sequence[Sequence[str]], pid_to_event: dict[str, str]
) -> float:
    """聚类级纯度(H-003 重设计): 全部连通成分纯度的按大小加权平均。

    只测种子成分会遗漏“其他成分是否被正确拆分”; 加权平均给出
    整张图的结构质量。孤立点成分(大小 1)纯度为 1.0。
    """
    total = sum(len(c) for c in components)
    if total == 0:
        return 0.0
    return sum(len(c) * cluster_purity(c, pid_to_event) for c in components) / total


def chain_purity(component_pids: Sequence[str], pid_to_chain: dict[str, int]) -> float:
    """成分的链纯度: 最大因果链占比(测“结构信号把链聚起来”)。

    与 cluster_purity 的唯一区别是 ground-truth 标签为链而非事件。
    """
    if not component_pids:
        return 0.0
    counts: dict[int, int] = {}
    for pid in component_pids:
        ch = pid_to_chain.get(pid, -1)
        counts[ch] = counts.get(ch, 0) + 1
    return max(counts.values()) / len(component_pids)


def mean_chain_purity(
    components: Sequence[Sequence[str]], pid_to_chain: dict[str, int]
) -> float:
    """聚类级链纯度: 全部成分的链纯度按大小加权平均。"""
    total = sum(len(c) for c in components)
    if total == 0:
        return 0.0
    return sum(len(c) * chain_purity(c, pid_to_chain) for c in components) / total


def reconstruction_metrics(
    component_pids: Sequence[str], true_event_pids: set[str]
) -> dict[str, float]:
    """以 ground-truth 事件为参照, 度量成分的重建质量。"""
    if not component_pids:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    component = set(component_pids)
    prec = len(component & true_event_pids) / len(component) if component else 0.0
    rec = len(component & true_event_pids) / len(true_event_pids) if true_event_pids else 0.0
    f1 = f1_at_k(prec, rec)
    return {"precision": prec, "recall": rec, "f1": f1}


def rank_stats(ranked: Sequence[str], relevant: set[str], k: int) -> dict[str, float]:
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


def ordered_path_recovery(
    retained_pids: Sequence[str],
    chains: Sequence[Sequence[str]],
    event_of: Callable[[str], str],
    mentions_of: Callable[[str], Sequence[str]],
) -> float:
    """有序路径恢复率: 检索保留点诱导的有向图对每条 ground-truth 链的
    最长相邻有序子路径长 / L(L 为该链事件数)。

    - retained_pids: 检索保留的候选点(含种子), 诱导图只在这些点上建边;
    - chains: ground-truth 链, 每条链 = 有序事件 id 序列 [e1..eL];
    - event_of: pid 到事件 id;
    - mentions_of: pid 到被提及 pid(引用方向 = 链前进方向, 与 meta["mentions"] 一致)。

    单条链: 事件 t 若在 retained 中有碎片则为"可及"; 相邻有序子路径
    e_i..e_j 成立当且仅当 i..j 内每个事件可及, 且每对相邻 (e_t, e_{t+1})
    存在 a 属于 e_t 的保留碎片, b 属于 e_{t+1} 的保留碎片, 使 b 属于
    mentions_of(a)。ℓ = 最长此类子路径长(无可及事件为 0), 恢复率 = ℓ / L。
    返回全链平均。这是检索层*有序*恢复新度量, 与 chain_connectivity
    (无向成对连通) 不同层、不同定义, 不可互换(EXP-005 度量消歧)。
    """
    if not chains:
        return 0.0
    retained = set(retained_pids)
    rates: list[float] = []
    for chain in chains:
        L = len(chain)
        if L == 0:
            continue
        ev_pids = {
            ev: {p for p in retained if event_of(p) == ev}
            for ev in chain
        }
        longest = 0
        cur = 0
        for t in range(L):
            ev = chain[t]
            if not ev_pids[ev]:
                longest = max(longest, cur)
                cur = 0
                continue
            if t == 0 or not _cite_link(ev_pids[chain[t - 1]], ev_pids[ev], mentions_of):
                longest = max(longest, cur)
                cur = 1
            else:
                cur += 1
        longest = max(longest, cur)
        rates.append(longest / L)
    return mean(rates)


def _cite_link(prev_pids: set[str], next_pids: set[str], mentions_of) -> bool:
    """相邻事件间是否存在引用边(前事件某碎片提及后事件某碎片)。"""
    for a in prev_pids:
        for b in mentions_of(a):
            if b in next_pids:
                return True
    return False
