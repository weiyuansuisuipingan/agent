from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class ContractFeatures:
    contract_title: str
    payment_days: int | None = None
    acceptance_days: int | None = None
    auto_renewal: bool = False
    termination_notice_days: int | None = None
    unlimited_liability: bool = False
    ip_assigned_to_customer: bool = False
    cross_border_data_transfer: bool = False
    weak_customer_delay_penalty: bool = False
    invoice_before_payment: bool = False
    extracted_clauses: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Finding:
    title: str
    severity: str
    reason: str
    recommendation: str
    related_clause: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiskAssessment:
    risk_score: int
    risk_level: str
    chain_risks: list[str]
    requires_human_review: bool

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ReviewResult:
    contract_name: str
    features: ContractFeatures
    findings: list[Finding]
    assessment: RiskAssessment
    markdown_report: str
    markdown_path: str
    json_path: str

    def to_dict(self) -> dict:
        return {
            "contract_name": self.contract_name,
            "features": self.features.to_dict(),
            "findings": [item.to_dict() for item in self.findings],
            "assessment": self.assessment.to_dict(),
            "markdown_path": self.markdown_path,
            "json_path": self.json_path,
        }
