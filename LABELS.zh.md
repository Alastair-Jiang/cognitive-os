< [English](./LABELS.md) | 简体中文 >

# Label 指南

本仓库所有 label 的含义与排序。**Rating 等级必带 emoji 前缀, 且沿低→高
渐变**; 其他维度内要么全带 emoji 要么全不带。Label 使用项目主语言(中文)。

## 类型 (Type)

| Label | 含义 |
|---|---|
| `🐛 缺陷` | 某个功能不符合预期 |
| `✨ 功能` | 新功能或请求 |
| `📚 文档` | 文档的改进或补充 |
| `❓ 问题` | 需要进一步信息的提问 |
| `🙋 寻求帮助` | 欢迎贡献者参与 |
| `🌱 新手友好` | 适合新贡献者入门 |

## 优先级 (P0 → P3)

| Label | 含义 |
|---|---|
| `🔴 P0` | 紧急: 数据丢失、安全绕过、崩溃循环、核心不可用 |
| `🟠 P1` | 高: 阻塞计划内工作, 需尽快处理 |
| `🟡 P2` | 中: 常规优先级 |
| `🟢 P3` | 低: 锦上添花 |

## 状态 (Status)

| Label | 含义 |
|---|---|
| `🚧 进行中` | 工作正在进行 |
| `🧱 被阻塞` | 被其他事项阻塞 |
| `✅ 待合并` | 已批准, 可以合并 |
| `🎉 已合并` | 已经合并 |
| `🚫 不修复` | 不会处理 |

## 模块 (Area)

| Label | 含义 |
|---|---|
| `area: retrieval` | 检索策略模块 (A/B/C 策略) |
| `area: anchors` | 锚点检测与多信号综合模块 |
| `area: graph` | 证据图与结构一致性模块 |
| `area: validation` | 渐进式验证与早停模块 |
| `area: dataset` | 合成语料生成与评测数据 |
| `area: research` | 研究工件: hypotheses/experiments/benchmarks/log |
| `area: docs` | 文档与仓库门面 |
| `area: nets` | 动态信息网(search_net)模块 |
| `area: stats` | 统计推断模块(perm/boot/效应量) |
| `area: benchmark` | 评测管线: scripts 实验运行器/configs/结果 JSON |
| `area: memory` | 个人记忆分层/控制面(E3, 未实施) |
| `area: agents` | 多 Agent/能力接口/编排(E4, 未实施) |

## Rating (PR 质量, 低 → 高)

> Rating 等级是本仓库唯一**强制带 emoji** 的 label 组 — 低→高渐变使
> 排序无歧义。主题: **研究证据等级**(贴合本项目假设→实验→结论的文化)。

| 位次 | Label | 含义 |
|---|---|---|
| 1 | `rating: 🔬 假设` | 最低档: 未经验证的假设/想法 |
| 2 | `rating: 🧪 原型` | 第二档: 有实现原型, 无实验结论 |
| 3 | `rating: 📊 实验` | 第三档: 已有实验数据支撑 |
| 4 | `rating: ✅ 已验证` | 第四档: 假设得到实验支持 |
| 5 | `rating: 🏆 里程碑` | 最高档: 确立阶段结论/研究里程碑 |

## 其他

> Maintained by repo-standardizer — 修改 label 时同步更新本文件。