# Contract Guardian Agent

`Contract Guardian Agent` 是一个面向企业销售、法务、财务协同场景的合同审查与回款风险预警项目。它不是示例里的代码重构方向，而是聚焦更贴近业务结果的合同风控场景：帮助团队更快识别付款周期过长、验收条件模糊、无限责任、知识产权归属异常、数据跨境等高风险条款，并自动生成审查报告。

## 项目价值

- 解决人工审查慢、标准不一致、经验难复用的问题
- 用多 Agent 流程把合同内容拆解、比对、推理、汇总
- 支持将“条款级风险”进一步组合成“现金流链路风险”和“合规链路风险”
- 生成可直接向业务方解释的审查结论和修改建议

## 多 Agent 设计

1. `DocumentParserAgent`
   - 解析合同文本
   - 抽取付款周期、验收周期、自动续约、责任边界、IP 归属等结构化特征
2. `ClauseComparisonAgent`
   - 将抽取结果与标准规则库进行逐项比对
   - 输出单点风险发现
3. `RiskReasoningAgent`
   - 对多个风险点进行长链路组合推理
   - 识别回款、合规、资产归属等复合风险
4. `ReportAgent`
   - 自动生成 Markdown 审查报告和 JSON 摘要
   - 给出处理建议和是否需要人工复核

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
|-- docs/
|   |-- application_answer.md
|   `-- project_overview.md
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

运行内置演示：

```bash
python main.py demo
```

运行测试：

```bash
python -m unittest discover -s tests -v
```

## 输出结果

程序会自动在 `outputs/` 目录中生成：

- `*_report.md`：可读性更强的审查报告
- `*_summary.json`：结构化风险摘要

## 适合如何讲给评审

你可以把这个项目包装成一个“企业合同审查与回款风控 Agent”，重点强调：

- 核心痛点：合同审查依赖人工，效率低，容易漏掉组合风险
- Agent 逻辑：不是单轮问答，而是多阶段、多角色协同
- 长链路推理：从条款识别升级到业务后果判断
- 业务价值：缩短审查时间，提升签约效率和回款安全

更完整的申报文案见 [docs/application_answer.md](F:\codex\agent\docs\application_answer.md)。
