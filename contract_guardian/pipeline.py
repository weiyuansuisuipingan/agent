from __future__ import annotations

from pathlib import Path

from contract_guardian.agents import ClauseComparisonAgent, DocumentParserAgent, ReportAgent, RiskReasoningAgent
from contract_guardian.models import ReviewResult


class ContractRiskPipeline:
    def __init__(self) -> None:
        self.parser_agent = DocumentParserAgent()
        self.comparison_agent = ClauseComparisonAgent()
        self.reasoning_agent = RiskReasoningAgent()
        self.report_agent = ReportAgent()

    def run(self, contract_path: Path, output_dir: Path) -> ReviewResult:
        text = contract_path.read_text(encoding="utf-8")
        contract_name = contract_path.stem

        features = self.parser_agent.run(contract_name, text)
        findings = self.comparison_agent.run(features)
        assessment = self.reasoning_agent.run(features, findings)
        markdown_report = self.report_agent.build_markdown(
            contract_name=contract_name,
            features=features,
            findings=findings,
            assessment=assessment,
        )
        markdown_path, json_path = self.report_agent.write_outputs(
            output_dir=output_dir,
            stem=contract_name,
            markdown_report=markdown_report,
            features=features,
            findings=findings,
            assessment=assessment,
        )

        return ReviewResult(
            contract_name=contract_name,
            features=features,
            findings=findings,
            assessment=assessment,
            markdown_report=markdown_report,
            markdown_path=markdown_path,
            json_path=json_path,
        )
