# Contract Guardian Agent

Contract Guardian Agent 是一个面向企业销售、法务、财务协同场景的合同审查与回款风险预警项目。它通过多 Agent 流程完成合同条款抽取、规则比对、复合风险推理和审查报告生成，帮助团队更快识别高风险合同并给出处理建议。

## Repository About

GitHub `About` 可直接使用下面这句：

`Multi-agent contract review and payment risk warning demo for sales, legal, and finance workflows.`

建议 Topics：

`multi-agent`, `contract-review`, `risk-analysis`, `python`, `legaltech`, `workflow-automation`

更多仓库介绍文案见 [repository_about.md](F:\codex\agent\docs\repository_about.md)。

## 核心价值

- 降低人工逐条审查的时间成本
- 提升合同审查标准的一致性
- 识别长账期、长验收、无限责任、IP 归属异常、数据跨境等关键风险
- 将单点条款风险组合成现金流、合规、责任等复合风险判断
- 自动生成 Markdown 报告和 JSON 摘要，便于接入审批流或知识库

## 多 Agent 流程

1. `DocumentParserAgent`
   - 解析合同文本
   - 抽取付款周期、验收周期、自动续约、责任边界、IP 归属等结构化字段
2. `ClauseComparisonAgent`
   - 按标准规则库逐项比对条款
   - 输出单点风险发现
3. `RiskReasoningAgent`
   - 组合多个风险信号做长链路推理
   - 识别回款、合规、责任失衡等复合风险
4. `ReportAgent`
   - 生成可读报告和结构化摘要
   - 给出是否建议人工复核

## 项目结构

```text
.
|-- contract_guardian/
|   |-- __init__.py
|   |-- agents.py
|   |-- models.py
|   |-- pipeline.py
|   `-- rules.py
|-- data/contracts/
|   |-- high_risk_saas_contract.txt
|   `-- low_risk_saas_contract.txt
|-- demo/
|   |-- app.js
|   |-- index.html
|   |-- styles.css
|   `-- data/reviews.json
|-- docs/
|   |-- project_overview.md
|   |-- repository_about.md
|   `-- solution_summary.md
|-- tests/
|   `-- test_pipeline.py
|-- main.py
`-- pyproject.toml
```

## 快速开始

要求：`Python 3.10+`

运行高风险样例：

```bash
python main.py review --input data/contracts/high_risk_saas_contract.txt
```

运行低风险样例：

```bash
python main.py review --input data/contracts/low_risk_saas_contract.txt
```

运行内置演示数据：

```bash
python main.py demo
```

运行测试：

```bash
python -m unittest discover -s tests -v
```

## 前端演示页

项目包含一个静态演示站，用于展示风险评分、关键条款、复合风险链路和多 Agent 流程。

![Contract Guardian Agent demo dashboard](docs/assets/demo-dashboard.JPG)

启动本地演示页：

```bash
python main.py serve-demo --port 4173
```

然后打开：

`http://127.0.0.1:4173`

## 输出结果

程序会自动在 `outputs/` 目录中生成：

- `*_report.md`：可读性更强的审查报告
- `*_summary.json`：结构化风险摘要

## 说明文档

- 项目摘要：[solution_summary.md](F:\codex\agent\docs\solution_summary.md)
- 项目总览：[project_overview.md](F:\codex\agent\docs\project_overview.md)
- 仓库 About 文案：[repository_about.md](F:\codex\agent\docs\repository_about.md)
