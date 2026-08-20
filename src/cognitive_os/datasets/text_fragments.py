"""文本碎片语料: 与 synthetic_events 同结构族的模板文本产出。

EXP-006 前置(ADR-0003 / H-006): 结构参数与 SyntheticCorpusConfig
同族(事件主题集 / 主来源 / 时间窗 / 因果链 / 提及抽取, 纪律对齐旧生成器);
碎片内容为中文模板文本(主题句 + 事件谓词句 + 因果链提及句),
文本到嵌入由外部 Embedder 完成(GPU 路径, BGE-M3), 本模块不产生向量
——点的 embedding 字段为空元组, 由嵌入遍填入(见协议层 CorpusView)。

几何意图: 事件有稳定的实体与谓词锚(事件内更近), 跨事件共享主题词
产生重叠(重叠但非平凡可分); within_event_noise 以给定概率向主题层
注入词表外干扰词——在真嵌入空间近似旧语料的「事件质心 + 噪声」结构。
半径与语义阈值标定不在本模块: EXP-006 检索前先记录相似度统计。
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

from ..types import InformationPoint, Query

TOPIC_LEXICON: tuple[str, ...] = (
    "供应链中断",
    "港口拥堵",
    "能源价格波动",
    "原材料短缺",
    "汇率风险",
    "物流延误",
    "政策监管调整",
    "市场需求转移",
    "产能调整",
    "跨境结算",
    "保险理赔争议",
    "气候异常影响",
)

ENTITY_LEXICON: tuple[str, ...] = (
    "恒桥集团",
    "澜海航运",
    "万象贸易",
    "北域制造",
    "青洲港务",
    "泗州能源",
    "南韵物流",
    "东岚科技",
    "熙源金融",
    "兆丰实业",
    "明仕咨询",
    "亚洲期货",
)

NOISE_LEXICON: tuple[str, ...] = (
    "地方庆典",
    "体育赛事",
    "校园开放日",
    "旅游旺季",
    "农产丰收",
    "艺术展览",
    "社区活动",
    "节日交通",
)

PHASE_LEXICON: tuple[str, ...] = (
    "初步发酵",
    "升级",
    "扩散",
    "相对缓和",
    "反弹",
    "局部爆发",
)

ACTION_LEXICON: tuple[str, ...] = (
    "应急预案",
    "供应调配",
    "价格重议",
    "库存盘点",
    "合同重签",
    "物流改道",
)

TOPIC_TEMPLATES: tuple[str, ...] = (
    "{ent}称{topic}走势仍在演变。",
    "就{topic}问题，{ent}发布了新的通报。",
    "{topic}进展影响{ent}的相关安排。",
    "{ent}内部简报将{topic}风险列为高优先级。",
)

NOISE_TEMPLATES: tuple[str, ...] = (
    "外部评论将该事与{noise}相提并论。",
    "报道同时提到{noise}因素，但未下结论。",
)

MENTION_TEMPLATES: tuple[str, ...] = (
    "报道称此次进展与{ref_topic}相关，详见{ref}。",
    "本报告延续此前论断，相关记录见{ref}。",
)


@dataclass
class TextFragmentConfig:
    n_events: int = 12
    fragments_per_event: int = 8
    n_topics: int = 5
    topics_per_event: int = 4  # 每事件激活主题数(与旧语料同义: 跨事件重叠带来歧义)
    within_event_noise: float = 0.5  # 碎片主题层被词表外干扰词扰动的概率
    time_horizon: float = 100.0
    event_span: float = 20.0
    source_count: int = 4
    source_min_weight: float = 0.6
    primary_source_prob: float = 0.6
    causal_chains: int = 0  # 与旧语料同义: 事件分链, 链内相邻事件互相提及
    mention_prob: float = 0.4
    seed: int = 20260819


class TextFragmentCorpus:
    """文本碎片语料: 点集合 + 事件 ground truth + 查询接口(不含向量)。"""

    def __init__(self, cfg: TextFragmentConfig | None = None):
        self.cfg = cfg or TextFragmentConfig()
        self.points: list[InformationPoint] = []
        self.events: dict[str, list[str]] = {}
        self._by_id: dict[str, InformationPoint] = {}
        self._event_start: dict[str, float] = {}
        self._event_topics: dict[str, tuple[str, ...]] = {}
        self._topics: tuple[str, ...] = ()
        self._build()

    # ------------------------------------------------------------------
    # 生成
    # ------------------------------------------------------------------
    def _build(self) -> None:
        cfg = self.cfg
        rng = random.Random(cfg.seed)
        n_top = min(cfg.n_topics, len(TOPIC_LEXICON))
        self._topics = tuple(rng.sample(TOPIC_LEXICON, n_top))
        source_weights = [
            cfg.source_min_weight
            + (1.0 - cfg.source_min_weight) * (i / max(cfg.source_count - 1, 1))
            for i in range(cfg.source_count)
        ]
        rng.shuffle(source_weights)  # 与旧语料同义: 不按索引序给权重

        # 因果链划分(与旧语料同算法): 事件按生成顺序均匀分链, 链内提后继
        chain_of_event: dict[str, int] = {}
        successor_fragments: dict[str, list[str]] = {}
        if cfg.causal_chains > 0:
            k = min(cfg.causal_chains, cfg.n_events)
            per = max(1, cfg.n_events // k)
            chains = [
                [f"evt{e:02d}" for e in range(c * per, min((c + 1) * per, cfg.n_events))]
                for c in range(k)
            ]
            for c, evs in enumerate(chains):
                for ev in evs:
                    chain_of_event[ev] = c
            for chain in chains:
                for idx, ev in enumerate(chain):
                    if idx + 1 < len(chain):
                        successor_fragments[ev] = [
                            f"{chain[idx + 1]}-f{f:02d}"
                            for f in range(cfg.fragments_per_event)
                        ]

        # 第一遍: 事件层(主题集 / 实体 / 谓词 / 主来源 / 时间窗)
        event_layer: list[dict[str, Any]] = []
        for e in range(cfg.n_events):
            event_id = f"evt{e:02d}"
            active = tuple(
                rng.sample(
                    list(self._topics),
                    min(cfg.topics_per_event, len(self._topics)),
                )
            )
            layer = {
                "entity": ENTITY_LEXICON[e % len(ENTITY_LEXICON)],
                "phase": rng.choice(PHASE_LEXICON),
                "action": rng.choice(ACTION_LEXICON),
                "primary": rng.randrange(cfg.source_count),
                "start": rng.uniform(0.0, max(cfg.time_horizon - cfg.event_span, 0.0)),
            }
            event_layer.append(layer)
            self.events[event_id] = []
            self._event_start[event_id] = layer["start"]
            self._event_topics[event_id] = active

        # 第二遍: 碎片层(模板文本 + 结构元数据)
        for e, layer in enumerate(event_layer):
            event_id = f"evt{e:02d}"
            for f in range(cfg.fragments_per_event):
                pid = f"{event_id}-f{f:02d}"
                topic_main = rng.choice(self._event_topics[event_id])
                topic_second = rng.choice(self._event_topics[event_id])
                noise_word = (
                    rng.choice(NOISE_LEXICON)
                    if rng.random() < cfg.within_event_noise
                    else None
                )
                if rng.random() < cfg.primary_source_prob:
                    src = layer["primary"]
                else:
                    src = rng.randrange(cfg.source_count)
                ts = layer["start"] + rng.uniform(0.0, cfg.event_span)
                meta: dict[str, Any] = {
                    "fragment_index": f,
                    "event_index": e,
                    "topics": [topic_main, topic_second],
                }
                mentions: list[str] = []
                if cfg.causal_chains > 0:
                    meta["chain_id"] = chain_of_event[event_id]
                    succ_pool = successor_fragments.get(event_id, [])
                    if succ_pool and rng.random() < cfg.mention_prob:
                        mentions = [rng.choice(succ_pool)]
                if mentions:
                    meta["mentions"] = mentions
                text = self._render(
                    rng, layer, topic_main, topic_second, noise_word, mentions
                )
                point = InformationPoint(
                    pid=pid,
                    event_id=event_id,
                    embedding=(),
                    timestamp=ts,
                    source=f"s{src}",
                    source_weight=source_weights[src],
                    text=text,
                    meta=meta,
                )
                self.points.append(point)
                self._by_id[pid] = point
                self.events[event_id].append(pid)

    def _render(self, rng, layer, topic_main, topic_second, noise_word, mentions) -> str:
        """主题句 + 事件谓词句 (+ 噪声句) (+ 因果链提及句)。"""
        parts = [
            rng.choice(TOPIC_TEMPLATES).format(ent=layer["entity"], topic=topic_main),
            f"事件阶段进入{layer['phase']}，{layer['entity']}启动{layer['action']}，重点涉及{topic_second}。",
        ]
        if noise_word is not None:
            parts.append(rng.choice(NOISE_TEMPLATES).format(noise=noise_word))
        for ref in mentions:
            ref_event = ref.split("-")[0]
            ref_topic = rng.choice(self._event_topics[ref_event])
            parts.append(
                rng.choice(MENTION_TEMPLATES).format(ref_topic=ref_topic, ref=ref)
            )
        return "".join(parts)

    # ------------------------------------------------------------------
    # 查询接口(语义镜像旧语料)
    # ------------------------------------------------------------------
    @property
    def point_ids(self) -> list[str]:
        return [p.pid for p in self.points]

    @property
    def topics(self) -> tuple[str, ...]:
        return self._topics

    def get(self, pid: str) -> InformationPoint:
        return self._by_id[pid]

    def event_of(self, pid: str) -> str:
        return self._by_id[pid].event_id

    def event_start(self, event_id: str) -> float:
        return self._event_start[event_id]

    def event_fragments(self, event_id: str) -> list[str]:
        return list(self.events.get(event_id, []))

    def mentions(self, pid: str) -> list[str]:
        return list(self._by_id[pid].meta.get("mentions", []))

    def chain_of(self, pid: str) -> int:
        return int(self._by_id[pid].meta.get("chain_id", -1))

    def observable_pids(self, t: float) -> list[str]:
        return [p.pid for p in self.points if p.timestamp <= t]

    def future_fragments(self, event_id: str, t: float) -> list[str]:
        return [
            pid
            for pid in self.events.get(event_id, [])
            if self.get(pid).timestamp > t
        ]

    def sample_queries(
        self,
        n: int,
        rng_seed: int = 1,
        truncate_frac: float | None = None,
    ) -> list[Query]:
        """与旧语料 sample_queries 同语义: 每查询取一个种子碎片。"""
        rng = random.Random(rng_seed)
        event_ids = sorted(self.events.keys())
        queries: list[Query] = []
        for i in range(n):
            event_id = rng.choice(event_ids)
            frags = self.events[event_id]
            if truncate_frac is not None:
                t_obs = (
                    self._event_start[event_id]
                    + truncate_frac * self.cfg.event_span
                )
                observable = [
                    pid for pid in frags if self.get(pid).timestamp <= t_obs
                ]
                if not observable:
                    observable = frags  # 极端情况兜底(与旧语料一致)
                seed = rng.choice(observable)
                allowed = self.observable_pids(t_obs)
            else:
                seed = rng.choice(frags)
                allowed = None
            queries.append(
                Query(
                    qid=f"q{i:03d}",
                    seed_pids=[seed],
                    event_id=event_id,
                    allowed_pids=allowed,
                )
            )
        return queries
