# ADR-0002: 零运行时依赖红线（pure stdlib）

- **状态**: Accepted（自仓库创始生效，本 ADR 追认并固化）
- **日期**: 2026-08-19
- **上下文**: `pyproject.toml` 声明 `dependencies = []`；numpy/pytest/ruff
  仅存在于 dev extras。EXP-003 曾因脚本带出第三方依赖倾向被 CI 拦截。

## 决策

  生产代码（`src/`、`scripts/`、`tests/`）只准使用 Python ≥3.10 标准库；
  任何第三方 import 都是不合规依赖，dev 工具链不在此限（不进运行时）。

## 理由

- 可复现性：实验结论必须"克隆即复现"，零安装是最低门槛；
- 替代方案"允许轻量依赖"被否决：依赖树一旦打开，统计/度量实现的
  版本漂移会侵蚀 EXP 结果的可比性。

## 后果

- **正面**: 复现链最短；CI 三版本矩阵直接暴露 stdlib 行为差异。
- **负面/代价**: 统计功效与索引结构受 stdlib 限制（如无稀疏矩阵）；
  E1 的 ANN 索引必须自研或以协议外挂形式存在。
- **不可逆点**: 研究结论全部建立在 stdlib 数值行为上；引入依赖需
  全量复跑既有基准并新开 ADR。

## 关联

  `docs/system_constitution.md` 第 3 条（诚实计量）; `pyproject.toml`。
