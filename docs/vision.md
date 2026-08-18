# Vision — 项目愿景

> 状态: **方向性文档**。本文描述的是"想研究什么", 不是"已经证明了什么"。
> 文中所有带 [H] 标记的论断都是 **Hypothesis(假设)**, 未经验证;
> 只有带 [V] 标记的才是当前已被本仓库实验验证的结论。
> 参见 [system_constitution.md](system_constitution.md) 第 1 条。

## 0. 项目定位

本项目是一个研究 **Personal Intelligence Infrastructure / Personal Cognitive OS**
的开放式实验平台。

**它不是一个 AGI 项目。** 项目最终是否能够向 AGI 靠近, 不应该由概念判断,
而应该由实验结果决定。AGI 是长期研究方向, 不是当前项目已经实现的结论。

正确的外部定位是:

> An experimental architecture for studying persistent, personalized,
> adaptive intelligence.

---

## 1. 思想起点: 一个信息安全问题

项目最初来源于一个信息安全问题:

假设一条有效信息在网络中被切分成多个碎片, 并通过不同节点、不同路径传播。
传统的信息处理方式可抽象为:

```text
信息采集 → 碎片收集 → 信息重组 → 完整验证 → 判断信息是否有效
```

问题在于: 如果必须等信息完整之后才能进行验证, 那么搜索、组合和验证过程
可能存在较高的时间与计算成本。

因此本项目提出一个反向问题 [H]:

> 是否可以在信息尚未完整形成之前, 就通过大量动态变化的"网"、局部锚点、
> 向量关系和渐进式验证, 提前识别哪些信息碎片更可能属于同一个有效信息结构?

---

## 2. 核心思想: Dynamic Information Net

把整个信息空间表示为一组点。每个点可以代表: 新闻片段、文档片段、数据记录、
时间事件、用户行为、搜索结果、金融数据、API 返回结果、Agent 中间结果。

传统方法倾向于:

```text
点 → 点 → 点 → 完整信息 → 验证
```

本项目希望研究 [H]:

```text
             Dynamic Net A
            ↙      ↓      ↘
        information space
             Dynamic Net B
            ↙      ↓      ↘
             Dynamic Net C
```

多个搜索网同时工作。每一个网可以拥有不同的搜索范围、时间窗口、特征权重、
相似度函数、信息来源权重、空间结构、采样策略、Anchor、搜索密度。
网本身也应该可以动态调整。

这里的"网"不是物理网络, 而是一种 **Dynamic Search / Retrieval Strategy**。

---

## 3. Progressive Validation

不要把验证完全放在搜索末端。研究 [H]:

```text
信息进入 → 局部判断 → 产生候选结构 → 更新置信度 → 继续搜索
→ 重新调整搜索空间 → 再次验证 → 最终形成高置信度结构
```

验证不是消失, 而是从 Final Validation 转变为
**Continuous / Progressive Validation**。

---

## 4. Anchor Mechanism

如果存在 N 个信息碎片, 完全两两比较可能接近 O(N²)。因此研究 [H]:

```text
大量信息点 → 寻找少量高置信度 Anchor → 围绕 Anchor 搜索 → 扩张候选结构
```

研究目标 [H]: **在不显著损失 Recall / Precision 的情况下, 降低搜索复杂度。**

Anchor 不是简单的"最相似点"。Anchor 可以综合: semantic similarity、
temporal consistency、source reliability、event consistency、
contextual similarity、causal consistency、historical evidence、user relevance。

---

## 5. 一个非常重要的风险: Local Similarity ≠ Global Same Event

**不要假设 Local Similarity = Global Same Event。**

例如: 苹果公司新品发布、苹果公司财报、苹果产区灾害, 可能共享大量相同语义。

```text
semantic similarity ≠ same information structure
```

因此系统必须研究 **Structure Consistency**, 而不仅仅是 Semantic Similarity,
逐步引入: 时间关系、来源关系、上下文、事件关系、因果关系、信息传播关系、
图结构一致性。

最终目标不是简单判断"两个点像不像?", 而是 [H]:

> "这些点共同组成某个有效信息结构的概率是多少?"

---

## 6. Information Topology

项目需要逐步从 Information Retrieval 发展到
**Information Structure Reconstruction**, 甚至 **Information Topology**。

这里不要求恢复原始文本。重点研究关系结构是否可以被恢复:

```text
A → B → C → D
```

对于量化研究尤其重要——很多时候信息之间的关系比原始文本本身更有价值 [H]。

---

## 7. Search Strategy Learning

系统最终不应该只学习 Answer, 而应该学习 **How to Search** [H]:

```text
Query → Search Strategy Selection → Dynamic Nets → Information Collection
→ Structure Reconstruction → Evidence Evaluation → Answer
```

需要研究 P(SearchStrategy | Query, Context, History), 而不仅仅是
P(Answer | Query)。

---

## 8. 二级搜索引擎: Search Intelligence Layer

第一阶段不要自己从零构建互联网搜索引擎。优先设计成位于现有搜索服务之上的
**Search Intelligence Layer**。未来可以通过合法、公开、官方或授权 API 接入
Bing / Google / 百度 / 新闻 API / 文档数据库 / 金融数据源 / GitHub /
用户授权的数据源。

本项目负责: Query Understanding → Search Strategy → Multiple Search Nets
→ Search APIs → Evidence Collection → Anchor Detection → Graph Construction
→ Evidence Ranking → AI Reasoning → Structured Report。

**不要把项目设计成单纯的"AI 搜索框"。**

---

## 9. Cognitive Recommendation

在搜索结果之后加入"猜你想搜 / 猜你想知道 / 下一步可能有价值的问题"。
但不要简单模仿短视频平台推荐算法。目标函数不应主要是 CTR / Watch Time /
Engagement, 而应研究 **Cognitive Utility / Information Gain / Task Completion /
Knowledge Gain / Decision Quality** [H]。

系统应该推荐: **下一条最有可能帮助用户完成当前认知任务的信息。**
最终推荐的不是简单相关内容, 而是 **认知路径 (Cognitive Path)** [H]。

例: 用户搜索"中信银行净息差" → 系统构建认知路径:

```text
净息差 → 银行盈利能力 → 资产负债结构 → 利率环境 → LPR → 银行估值 → 银行板块 → 中信银行
```

---

## 10. Personal Memory(分层, 且要求行为证据)

Memory 必须分层:

| Level | 名称 | 内容 |
|---|---|---|
| L1 | Interest Memory | 用户长期关注什么 |
| L2 | Knowledge Memory | 用户已掌握什么(避免重复解释) |
| L3 | Thinking Strategy Memory | 用户喜欢如何解决问题(抽象/类比/数学化/先例后理/先系统后实现) |
| L4 | Meta-Cognitive Memory | 哪些问题易产生洞见/错误、什么证据容易改变判断、哪些认知盲区 |

**注意 [V-设计约束]: 不要默认这些特征是事实, 必须来自足够的行为证据。
系统不能把模型推断包装成用户事实**(见 system_constitution.md 第 4 条)。

---

## 11. Personal Cognitive Model(防回声室)

```text
Public Information → Personal Memory → Personal Retrieval Strategy
→ Personal Cognitive Model → Personal Search
```

目标 [H]: 不同用户面对相同问题, 可以获得不同的搜索路径。

**但必须避免 Personalization → Echo Chamber。** 系统应该主动保留:
Counter Evidence、Diverse Sources、Contradictory Views、Uncertainty、
Alternative Hypotheses。

---

## 12. Multi-Agent 与 Capability Interface

后续可以加入不同 AI 能力: Research / Search / Coding / Data / Reasoning /
Planning / Report / Execution Agent。不同模型(OpenAI / DeepSeek / Anthropic /
本地模型)可以作为可插拔能力, 但**不要把具体厂商写死在核心架构**。

核心是 Capability Interface, 而不是 Model Dependency:

```text
Model Provider → Capability Adapter → Agent → Orchestrator
```

---

## 13. Cognitive OS: 核心闭环

```text
Perception → Retrieval → Memory → Reasoning → Planning → Action → Feedback → Learning ↺
```

这不是普通聊天机器人。重点研究: 一个系统如何持续理解用户、环境、任务和历史。

---

## 14. Biomimetic Architecture(组织原则, 不是复制神经元)

研究 **Brain-inspired organizational principles**:

| Biological Concept | System Concept |
|---|---|
| Sensory System | Information Acquisition |
| Hippocampus | Episodic Memory |
| Cortex | Knowledge Representation |
| Prefrontal Cortex | Planning |
| Attention | Compute Allocation |
| Association | Information Linking |
| Long-term Memory | Persistent Memory |
| Working Memory | Context |
| Neural Connections | Module Communication |

重点不是复制结构, 而是研究 **Information Flow** [H]:
什么信息进入工作记忆/长期记忆? 什么信息被遗忘? 什么信息获得更多计算资源?
哪些模块之间应该通信? 哪些信息应该被阻断?

---

## 15. Dynamic Cognitive Graph

将系统抽象成 G = (V, E, W): V = modules / information nodes,
E = relationships, W = dynamic weights。连接权重根据反馈变化:

```text
W_{ij}^{t+1} = W_{ij}^{t} + ΔW
```

未来研究 [H]: 是否可以让系统的"认知结构"随着使用而变化。

---

## 16. World Model 与 Digital → Social → Physical

如果系统进一步发展, 需要建立 World Model: 将人、事件、时间、地点、物体、
社会关系、因果关系、数字信息、物理状态放入统一关系空间。
最终系统理解的不是"网页", 而是 **世界中的事件与关系**。

```text
Human ↕ Cognitive OS ↕ Digital World ↕ Social World ↕ Physical World
```

长期可以连接: Digital(Search/Internet/Documents/News/Code/Financial Data)
→ Cognitive(Memory/Reasoning/Planning/Agents)
→ Social(Finance/Healthcare/Insurance/Transportation/Education/Public Services)
→ Physical(Robotics/IoT/Smart Devices/Autonomous Systems)。

未来设计统一能力接口: Search / Reason / Remember / Plan / Navigate /
Communicate / Manipulate / Observe。机器人可以成为
**Physical Execution Interface**:

```text
Cognitive Core → Capability API → Robot → Physical Action
→ Observation → Feedback → Cognitive Core
```

---

## 17. 项目最终要回答的问题

最终探索的问题不是"能不能做一个比 ChatGPT 更大的模型", 而是:

> **能不能构建一个能够理解用户、理解信息、理解任务、理解环境, 并通过持续记忆、
> 动态检索、推理、规划、执行和反馈逐渐改变自身工作方式的个人智能系统?**

其核心闭环:

```text
Understand → Search → Connect → Remember → Reason → Plan → Act → Observe → Learn → Adapt ↺
```

**这个 Repository 的意义, 是把上述愿景拆解成可以被实现、测试、反驳、修改、
迭代和最终证明或否定的研究问题。** 第一目标不是 AGI,
第一目标是证明第一块砖是否成立。
