from __future__ import annotations

import json
import re
from pathlib import Path

from contract_guardian.models import ContractFeatures, Finding, RiskAssessment
from contract_guardian.rules import SEVERITY_SCORES, STANDARD_THRESHOLDS, normalize_score, risk_level_from_score


class DocumentParserAgent:
    """Extracts structured features from raw contract text."""

    def run(self, contract_name: str, text: str) -> ContractFeatures:
        normalized = self._normalize(text)
        features = ContractFeatures(contract_title=contract_name)

        payment_days = self._extract_days(
            normalized,
            [
                r"(?:验收后|发票开具后|收到发票后|回款周期为|付款期限为|付款应在)[^\n。；;]{0,20}?(\d{1,3})日",
                r"(\d{1,3})日内支付",
            ],
        )
        acceptance_days = self._extract_days(
            normalized,
            [
                r"(?:验收期限为|验收应在|验收周期为)[^\n。；;]{0,20}?(\d{1,3})日",
                r"交付后(\d{1,3})日内完成验收",
            ],
        )
        termination_notice_days = self._extract_days(
            normalized,
            [
                r"提前(\d{1,3})日书面通知",
            ],
        )

        features.payment_days = payment_days
        features.acceptance_days = acceptance_days
        features.termination_notice_days = termination_notice_days
        features.auto_renewal = any(
            keyword in normalized for keyword in ["自动续约", "自动顺延", "续展一年", "续期一年"]
        )
        features.unlimited_liability = any(
            keyword in normalized
            for keyword in ["承担全部责任", "无限责任", "不设赔偿上限", "赔偿责任不受限制"]
        )
        features.ip_assigned_to_customer = any(
            keyword in normalized
            for keyword in ["知识产权归客户所有", "全部知识产权归甲方所有", "著作权归客户所有"]
        )
        features.cross_border_data_transfer = self._has_affirmative_phrase(
            normalized,
            ["传输至境外", "境外服务器", "跨境传输", "海外存储"],
            ["不得", "禁止", "未经审批不得", "应在境内", "境内环境完成"],
        )
        features.weak_customer_delay_penalty = any(
            keyword in normalized
            for keyword in ["逾期付款违约金按每日0.01%", "逾期付款违约金按日万分之一", "客户逾期付款不承担其他责任"]
        )
        features.invoice_before_payment = self._has_affirmative_phrase(
            normalized,
            ["先开票后付款", "以发票开具为付款前提", "开票后方可付款"],
            [],
        )

        features.extracted_clauses = {
            "payment": self._extract_sentence(normalized, ["付款", "回款", "发票"]),
            "acceptance": self._extract_sentence(normalized, ["验收"]),
            "renewal": self._extract_sentence(normalized, ["续约", "顺延"]),
            "liability": self._extract_sentence(normalized, ["责任", "赔偿"]),
            "ip": self._extract_sentence(normalized, ["知识产权", "著作权"]),
            "data": self._extract_sentence(normalized, ["跨境", "境外", "海外"]),
        }
        return features

    def _normalize(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.strip())

    def _extract_days(self, text: str, patterns: list[str]) -> int | None:
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return None

    def _extract_sentence(self, text: str, keywords: list[str]) -> str:
        parts = re.split(r"[。；;]", text)
        for part in parts:
            if any(keyword in part for keyword in keywords):
                return part.strip()
        return "未提取到明确条款"

    def _has_affirmative_phrase(
        self,
        text: str,
        positive_keywords: list[str],
        negative_keywords: list[str],
    ) -> bool:
        parts = re.split(r"[。；;]", text)
        for part in parts:
            if any(keyword in part for keyword in positive_keywords):
                if any(negative in part for negative in negative_keywords):
                    continue
                return True
        return False


class ClauseComparisonAgent:
    """Compares extracted features with the standard rule set."""

    def run(self, features: ContractFeatures) -> list[Finding]:
        findings: list[Finding] = []

        if features.payment_days and features.payment_days > STANDARD_THRESHOLDS["max_payment_days"]:
            findings.append(
                Finding(
                    title="付款周期过长",
                    severity="high",
                    reason=f"当前付款周期为 {features.payment_days} 日，超过建议阈值 {STANDARD_THRESHOLDS['max_payment_days']} 日。",
                    recommendation="建议改为里程碑付款或将回款周期压缩至 30-45 日。",
                    related_clause=features.extracted_clauses.get("payment"),
                )
            )

        if features.acceptance_days and features.acceptance_days > STANDARD_THRESHOLDS["max_acceptance_days"]:
            findings.append(
                Finding(
                    title="验收周期偏长",
                    severity="medium",
                    reason=f"验收周期为 {features.acceptance_days} 日，容易推迟开票与收款。",
                    recommendation="建议限定验收时点，并增加逾期视为默认验收条款。",
                    related_clause=features.extracted_clauses.get("acceptance"),
                )
            )

        if features.auto_renewal:
            findings.append(
                Finding(
                    title="存在自动续约条款",
                    severity="medium",
                    reason="自动续约可能在业务未及时跟进时形成持续义务。",
                    recommendation="建议增加明确的续约确认机制或缩短通知周期。",
                    related_clause=features.extracted_clauses.get("renewal"),
                )
            )

        if features.termination_notice_days and features.termination_notice_days > STANDARD_THRESHOLDS["max_termination_notice_days"]:
            findings.append(
                Finding(
                    title="终止通知周期较长",
                    severity="medium",
                    reason=f"合同要求提前 {features.termination_notice_days} 日通知终止，灵活性较弱。",
                    recommendation="建议缩短为 15-30 日，避免错过终止窗口。",
                    related_clause=features.extracted_clauses.get("renewal"),
                )
            )

        if features.unlimited_liability:
            findings.append(
                Finding(
                    title="赔偿责任未封顶",
                    severity="critical",
                    reason="合同存在无限责任或未设置赔偿上限，容易造成不可控损失。",
                    recommendation="建议将赔偿责任上限限定为合同金额或最近 12 个月已支付服务费。",
                    related_clause=features.extracted_clauses.get("liability"),
                )
            )

        if features.ip_assigned_to_customer:
            findings.append(
                Finding(
                    title="知识产权归属异常",
                    severity="high",
                    reason="合同将成果或著作权整体归属客户，可能损害平台复用与二次商业化能力。",
                    recommendation="建议区分预有知识产权、通用能力和项目定制交付物。",
                    related_clause=features.extracted_clauses.get("ip"),
                )
            )

        if features.cross_border_data_transfer:
            findings.append(
                Finding(
                    title="存在数据跨境风险",
                    severity="high",
                    reason="合同涉及境外传输或境外存储，可能触发额外的数据合规义务。",
                    recommendation="建议补充脱敏、最小化、数据地域和合规审批要求。",
                    related_clause=features.extracted_clauses.get("data"),
                )
            )

        if features.weak_customer_delay_penalty:
            findings.append(
                Finding(
                    title="客户逾期付款约束偏弱",
                    severity="medium",
                    reason="客户逾期付款责任偏轻，难以形成有效支付约束。",
                    recommendation="建议提高违约金标准，或增加暂停服务等补救措施。",
                    related_clause=features.extracted_clauses.get("payment"),
                )
            )

        if features.invoice_before_payment:
            findings.append(
                Finding(
                    title="付款依赖开票前置",
                    severity="low",
                    reason="若付款以开票为前置条件，可能在争议场景下进一步拖慢回款。",
                    recommendation="建议将开票条件与验收节点、付款节点同时明确。",
                    related_clause=features.extracted_clauses.get("payment"),
                )
            )

        return findings


class RiskReasoningAgent:
    """Builds chain risks from isolated findings."""

    def run(self, features: ContractFeatures, findings: list[Finding]) -> RiskAssessment:
        score = 0
        chain_risks: list[str] = []

        for finding in findings:
            score += SEVERITY_SCORES[finding.severity]

        if (features.payment_days or 0) >= 60 and (features.acceptance_days or 0) >= 30:
            chain_risks.append(
                "现金流链路风险：长账期与长验收周期叠加，会同时推迟确认收入、开票和回款。"
            )
            score += 15

        if features.unlimited_liability and features.ip_assigned_to_customer:
            chain_risks.append(
                "资产与赔偿双重风险：在知识产权让渡的同时承担无限责任，项目收益与风险严重失衡。"
            )
            score += 20

        if features.cross_border_data_transfer and features.ip_assigned_to_customer:
            chain_risks.append(
                "合规复合风险：数据跨境与成果归属客户同时存在，容易引发额外合规和审计压力。"
            )
            score += 10

        if features.auto_renewal and (features.termination_notice_days or 0) > 30:
            chain_risks.append(
                "续约锁定风险：自动续约配合较长终止通知期，可能导致团队错过退出窗口。"
            )
            score += 10

        final_score = normalize_score(score)
        risk_level = risk_level_from_score(final_score)
        requires_human_review = risk_level in {"high", "critical"}

        return RiskAssessment(
            risk_score=final_score,
            risk_level=risk_level,
            chain_risks=chain_risks,
            requires_human_review=requires_human_review,
        )


class ReportAgent:
    """Creates human-readable and machine-readable outputs."""

    def build_markdown(
        self,
        contract_name: str,
        features: ContractFeatures,
        findings: list[Finding],
        assessment: RiskAssessment,
    ) -> str:
        lines = [
            f"# 合同审查报告：{contract_name}",
            "",
            "## 一、审查结论",
            f"- 风险等级：`{assessment.risk_level}`",
            f"- 风险评分：`{assessment.risk_score}` / 100",
            f"- 是否建议人工复核：`{'是' if assessment.requires_human_review else '否'}`",
            "",
            "## 二、结构化抽取",
            f"- 付款周期：`{features.payment_days if features.payment_days is not None else '未识别'}` 日",
            f"- 验收周期：`{features.acceptance_days if features.acceptance_days is not None else '未识别'}` 日",
            f"- 自动续约：`{'是' if features.auto_renewal else '否'}`",
            f"- 终止通知期：`{features.termination_notice_days if features.termination_notice_days is not None else '未识别'}` 日",
            f"- 无限责任：`{'是' if features.unlimited_liability else '否'}`",
            f"- 知识产权归客户：`{'是' if features.ip_assigned_to_customer else '否'}`",
            f"- 数据跨境：`{'是' if features.cross_border_data_transfer else '否'}`",
            "",
            "## 三、单点风险发现",
        ]

        if findings:
            for index, finding in enumerate(findings, start=1):
                lines.extend(
                    [
                        f"### {index}. {finding.title}",
                        f"- 严重级别：`{finding.severity}`",
                        f"- 原因：{finding.reason}",
                        f"- 建议：{finding.recommendation}",
                        f"- 关联条款：{finding.related_clause or '无'}",
                        "",
                    ]
                )
        else:
            lines.extend(["- 未发现明显超阈值风险。", ""])

        lines.append("## 四、长链路推理")
        if assessment.chain_risks:
            for item in assessment.chain_risks:
                lines.append(f"- {item}")
        else:
            lines.append("- 未触发复合风险链。")
        lines.extend(
            [
                "",
                "## 五、处理建议",
                "- 对 `high` 和 `critical` 级别合同，建议进入法务人工复核。",
                "- 优先推进付款、验收、责任、IP 归属四类条款修订。",
                "- 将本次审查结果沉淀回规则库，持续提升后续自动审查质量。",
                "",
                "## 六、Agent 流程回放",
                "- `DocumentParserAgent`：完成条款抽取与字段结构化。",
                "- `ClauseComparisonAgent`：对照标准阈值完成单点比对。",
                "- `RiskReasoningAgent`：识别复合风险和业务影响链路。",
                "- `ReportAgent`：生成可交付的审查结论。",
            ]
        )
        return "\n".join(lines)

    def write_outputs(
        self,
        output_dir: Path,
        stem: str,
        markdown_report: str,
        features: ContractFeatures,
        findings: list[Finding],
        assessment: RiskAssessment,
    ) -> tuple[str, str]:
        output_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = output_dir / f"{stem}_report.md"
        json_path = output_dir / f"{stem}_summary.json"

        markdown_path.write_text(markdown_report, encoding="utf-8")
        json_path.write_text(
            json.dumps(
                {
                    "features": features.to_dict(),
                    "findings": [item.to_dict() for item in findings],
                    "assessment": assessment.to_dict(),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        return str(markdown_path), str(json_path)
