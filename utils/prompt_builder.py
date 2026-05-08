from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass
class PromptParts:
    role: str = ""
    context: str = ""
    task: str = ""
    output_format: str = ""
    constraints: str = ""
    evaluation: str = ""


def _clean(value: str | None) -> str:
    return (value or "").strip()


def build_rctofe_prompt(parts: PromptParts | dict) -> str:
    """Build a structured R-C-T-O-F-E prompt."""
    if isinstance(parts, dict):
        parts = PromptParts(**{k: _clean(v) for k, v in parts.items() if k in PromptParts.__annotations__})

    sections = []
    if _clean(parts.role):
        sections.append(f"ROLE\n{_clean(parts.role)}")
    if _clean(parts.context):
        sections.append(f"CONTEXT\n{_clean(parts.context)}")
    if _clean(parts.task):
        sections.append(f"TASK\n{_clean(parts.task)}")
    if _clean(parts.output_format):
        sections.append(f"OUTPUT FORMAT\n{_clean(parts.output_format)}")
    if _clean(parts.constraints):
        sections.append(f"CONSTRAINTS\n{_clean(parts.constraints)}")
    if _clean(parts.evaluation):
        sections.append(f"EVALUATION CRITERIA\n{_clean(parts.evaluation)}")
    if not sections:
        return ""
    return "\n\n".join(sections)


def build_nudge_prompt(context: str, nudges: Iterable[str], final_instruction: str = "") -> str:
    nudges = [n.strip() for n in nudges if n and n.strip()]
    blocks = []
    if context.strip():
        blocks.append(f"CONTEXT\n{context.strip()}")
    if nudges:
        blocks.append("SELECTED INSTRUCTIONS\n" + "\n".join(f"- {n}" for n in nudges))
    if final_instruction.strip():
        blocks.append(f"FINAL TASK\n{final_instruction.strip()}")
    if not blocks:
        return ""
    return "\n\n".join(blocks)


def build_document_prompt(task: str, document_text: str, audience: str, additional_constraints: str = "") -> str:
    base = f"""You are an executive assistant and policy-aware management analyst.

Audience: {audience.strip() or 'senior executive audience'}

Task: {task.strip()}

Important instructions:
- Use only the information contained in the document text below.
- Do not invent facts, figures, rules, names, or dates.
- Mark uncertain or missing points clearly.
- Flag anything that requires human verification.
- Keep the tone formal, concise, and suitable for senior leadership.
""".strip()
    if additional_constraints.strip():
        base += f"\n- Additional constraints: {additional_constraints.strip()}"
    base += "\n\nDOCUMENT TEXT\n" + document_text.strip()
    return base


def build_capstone_plan(data: dict) -> str:
    lines = [
        "# Gen AI-Enabled Executive Workflow Action Plan",
        "",
        f"**Selected workflow:** {data.get('workflow', '').strip()}",
        "",
        "## 1. Current Workflow",
        data.get('current_workflow', '').strip() or "Not specified.",
        "",
        "## 2. Current Pain Points",
        data.get('pain_points', '').strip() or "Not specified.",
        "",
        "## 3. Proposed AI-Enabled Workflow",
        data.get('ai_workflow', '').strip() or "Not specified.",
        "",
        "## 4. Free/Free-Tier Tools",
        data.get('tools', '').strip() or "Not specified.",
        "",
        "## 5. Prompt Pack",
        data.get('prompts', '').strip() or "Not specified.",
        "",
        "## 6. Human Review Points",
        data.get('human_review', '').strip() or "Not specified.",
        "",
        "## 7. Risk Safeguards",
        data.get('risks', '').strip() or "Not specified.",
        "",
        "## 8. Expected Benefits",
        data.get('benefits', '').strip() or "Not specified.",
        "",
        "## 9. 30-Day Pilot Plan",
        data.get('pilot_plan', '').strip() or "Not specified.",
        "",
        "## 10. Success Metrics",
        data.get('metrics', '').strip() or "Not specified.",
    ]
    return "\n".join(lines)
