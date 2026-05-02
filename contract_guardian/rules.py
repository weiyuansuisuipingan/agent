STANDARD_THRESHOLDS = {
    "max_payment_days": 45,
    "max_acceptance_days": 15,
    "max_termination_notice_days": 30,
}


SEVERITY_SCORES = {
    "low": 10,
    "medium": 20,
    "high": 35,
    "critical": 50,
}


def normalize_score(score: int) -> int:
    if score < 0:
        return 0
    if score > 100:
        return 100
    return score


def risk_level_from_score(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"
