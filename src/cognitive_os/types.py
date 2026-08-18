"""核心数据类型: 信息点 / 查询 / 证据 / 检索结果。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

# 向量表示: 一维浮点元组(纯标准库, 零依赖)
Embedding = Tuple[float, ...]


@dataclass
class InformationPoint:
    """信息空间中的一个碎片。

    一个点可以代表: 新闻片段 / 文档片段 / 数据记录 / 时间事件 /
    用户行为 / 搜索结果 / 金融数据 / API 返回 / Agent 中间结果。
    本原型中向量为合成生成。
    """

    pid: str  # 稳定点 id, 如 "e03-f05"
    event_id: str  # ground-truth 结构标签(仅用于评测, 检索时不可见)
    embedding: Embedding
    timestamp: float  # 碎片可被观测的时间
    source: str  # 来源 id
    source_weight: float  # 来源可靠性, (0, 1]
    text: str = ""  # 可选文本片段
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Query:
    """一次检索请求。

    seed_pids: 已观测到的种子碎片(查询输入)。
    event_id: 目标事件的 ground truth(仅用于评测)。
    allowed_pids: 可观测点集合; None 表示全语料可见
        (用于模拟"信息尚未完整"的截断场景)。
    """

    qid: str
    seed_pids: List[str]
    event_id: str = ""
    allowed_pids: Optional[List[str]] = None

    def is_allowed(self, pid: str) -> bool:
        if self.allowed_pids is None:
            return True
        return pid in self.allowed_pids


@dataclass
class Evidence:
    """检索过程中累积的候选点证据。

    score: 组合证据分(语义/来源/时间/结构加权)。
    confidence: 渐进式验证给出的置信度(跨网共识 + 证据强度)。
    votes: 支持该候选的网数(共识强度)。
    """

    pid: str
    score: float = 0.0
    semantic_sim: float = 0.0
    source_evidence: float = 0.0
    temporal_evidence: float = 0.0
    structural_evidence: float = 0.0
    confidence: float = 0.0
    votes: int = 0
    rounds_seen: int = 0

    def as_dict(self) -> Dict[str, Any]:
        return {
            "pid": self.pid,
            "score": round(self.score, 6),
            "semantic_sim": round(self.semantic_sim, 6),
            "source_evidence": round(self.source_evidence, 6),
            "temporal_evidence": round(self.temporal_evidence, 6),
            "structural_evidence": round(self.structural_evidence, 6),
            "confidence": round(self.confidence, 6),
            "votes": self.votes,
            "rounds_seen": self.rounds_seen,
        }


@dataclass
class RetrievalResult:
    """检索结果: 排序、证据、效率计数。"""

    qid: str
    strategy: str
    ranked_pids: List[str] = field(default_factory=list)
    scores: List[float] = field(default_factory=list)
    evidence: Dict[str, Evidence] = field(default_factory=dict)
    iterations: int = 0
    similarity_calls: int = 0  # 计算/API 调用成本代理
    index_lookups: int = 0
    latency_ms: float = 0.0
    early_stopped: bool = False
    notes: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "qid": self.qid,
            "strategy": self.strategy,
            "ranked_pids": self.ranked_pids,
            "scores": [round(s, 6) for s in self.scores],
            "evidence": {pid: ev.as_dict() for pid, ev in self.evidence.items()},
            "iterations": self.iterations,
            "similarity_calls": self.similarity_calls,
            "index_lookups": self.index_lookups,
            "latency_ms": round(self.latency_ms, 4),
            "early_stopped": self.early_stopped,
            "notes": self.notes,
        }
