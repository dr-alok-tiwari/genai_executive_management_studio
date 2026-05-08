from __future__ import annotations


def score_rctofe(parts: dict) -> tuple[int, list[str]]:
    checks = {
        "role": "Add a clear role, e.g., executive assistant, policy analyst, risk analyst.",
        "context": "Add specific context so the AI understands the managerial situation.",
        "task": "State the exact task and expected action.",
        "output_format": "Specify the output format, e.g., table, memo, checklist, email.",
        "constraints": "Add constraints such as no invented facts, formal tone, concise output.",
        "evaluation": "Add evaluation criteria such as accuracy, feasibility, risk awareness, actionability.",
    }
    score = 0
    feedback = []
    for key, advice in checks.items():
        if str(parts.get(key, "")).strip():
            score += 1
        else:
            feedback.append(advice)
    return score, feedback


def prompt_score_label(score: int, max_score: int = 6) -> str:
    if max_score == 6:
        if score <= 2:
            return "Needs improvement"
        if score <= 4:
            return "Good start"
        return "Executive-ready prompt"
    pct = (score / max_score) * 100 if max_score else 0
    if pct < 40:
        return "Needs improvement"
    if pct < 70:
        return "Good start"
    return "Strong"


def readiness_interpretation(score: int) -> tuple[str, str]:
    if score <= 30:
        return "Not ready", "Strengthen data safety, use-case clarity, human review, and governance before using Gen AI in formal workflows."
    if score <= 60:
        return "Partially ready", "Suitable for awareness and small experiments, but controls and review mechanisms need improvement."
    if score <= 80:
        return "Ready for pilot", "Begin with low-risk use cases using dummy or approved data, and document review procedures."
    return "Ready for controlled implementation", "Proceed with controlled scaling, clear accountability, audit trail, and periodic review."
