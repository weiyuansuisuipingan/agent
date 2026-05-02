from __future__ import annotations

import unittest
from pathlib import Path

from contract_guardian.pipeline import ContractRiskPipeline


class ContractRiskPipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.pipeline = ContractRiskPipeline()
        self.output_dir = Path("test_outputs")
        self.output_dir.mkdir(exist_ok=True)

    def test_high_risk_contract_triggers_human_review(self) -> None:
        result = self.pipeline.run(
            Path("data/contracts/high_risk_saas_contract.txt"),
            self.output_dir,
        )
        self.assertIn(result.assessment.risk_level, {"high", "critical"})
        self.assertTrue(result.assessment.requires_human_review)
        self.assertGreaterEqual(result.assessment.risk_score, 80)

    def test_low_risk_contract_scores_lower_than_high_risk(self) -> None:
        high_risk = self.pipeline.run(
            Path("data/contracts/high_risk_saas_contract.txt"),
            self.output_dir,
        )
        low_risk = self.pipeline.run(
            Path("data/contracts/low_risk_saas_contract.txt"),
            self.output_dir,
        )
        self.assertLess(low_risk.assessment.risk_score, high_risk.assessment.risk_score)
        self.assertEqual(low_risk.assessment.risk_level, "low")


if __name__ == "__main__":
    unittest.main()
