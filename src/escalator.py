import json
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any

from . import config


@dataclass
class EscalationDecision:
    escalated: bool
    reasons: List[str] = field(default_factory=list)


def _contains_any(text: str, keywords: List[str]) -> List[str]:
    text_lower = text.lower()
    matched = []

    for kw in keywords:
        pattern = r"\b" + re.escape(kw)

        if re.search(pattern, text_lower):
            matched.append(kw)

    return matched


def check_escalation(
    user_message: str,
    retrieved_chunks: List[Dict[str, Any]],
    persona: str,
    consecutive_unresolved_turns: int = 0,
    cfg: config.AppConfig = config.CONFIG,
) -> EscalationDecision:

    reasons = []

    if not retrieved_chunks:
        reasons.append(
            "No relevant knowledge-base content was retrieved for this query."
        )

    best_score = max(
        (
            c["score"]
            for c in retrieved_chunks
            if c.get("score") is not None
        ),
        default=0.0,
    )

    if (
        retrieved_chunks
        and best_score < cfg.retrieval_confidence_threshold
    ):
        reasons.append(
            f"Top retrieval confidence ({best_score:.2f}) is below "
            f"the configured threshold "
            f"({cfg.retrieval_confidence_threshold})."
        )

    matched_sensitive = _contains_any(
        user_message,
        cfg.sensitive_keywords,
    )

    if matched_sensitive:
        reasons.append(
            "Sensitive/account-critical topic detected "
            f"(matched: {', '.join(matched_sensitive[:3])})."
        )

    if (
        persona == "Frustrated User"
        and consecutive_unresolved_turns
        >= cfg.max_unresolved_turns
    ):
        reasons.append(
            "User has remained in a frustrated, unresolved state "
            f"for {consecutive_unresolved_turns} consecutive turns."
        )

    matched_human_request = _contains_any(
        user_message,
        [
            "speak to a human",
            "speak to a manager",
            "real person",
            "actual human",
        ],
    )

    if matched_human_request:
        reasons.append(
            "User explicitly requested a human agent."
        )

    return EscalationDecision(
        escalated=len(reasons) > 0,
        reasons=reasons,
    )


def build_handoff_summary(
    persona: str,
    user_message: str,
    conversation_history: List[Dict[str, str]],
    retrieved_chunks: List[Dict[str, Any]],
    attempted_steps: List[str],
    escalation_reasons: List[str],
) -> Dict[str, Any]:
    """Create handoff summary."""

    issue_summary = user_message.strip()

    if len(issue_summary) > 220:
        issue_summary = issue_summary[:217] + "..."

    documents_used = (
        sorted({c["source"] for c in retrieved_chunks})
        if retrieved_chunks
        else []
    )

    best_score = max(
        (
            c["score"]
            for c in retrieved_chunks
            if c.get("score") is not None
        ),
        default=0.0,
    )

    recommendation = _recommend_next_step(
        escalation_reasons,
        persona,
    )

    return {
        "persona": persona,
        "issue": issue_summary,
        "conversation_history": conversation_history,
        "documents_used": documents_used,
        "retrieval_confidence": round(best_score, 4),
        "attempted_steps": attempted_steps,
        "escalation_reasons": escalation_reasons,
        "recommendation": recommendation,
    }


def _recommend_next_step(
    escalation_reasons: List[str],
    persona: str,
) -> str:

    joined = " ".join(escalation_reasons).lower()

    if (
        "sensitive" in joined
        or "billing" in joined
        or "legal" in joined
    ):
        return (
            "Route to Billing/Trust & Safety specialist "
            "for manual review of the account-sensitive request."
        )

    if (
        "no relevant" in joined
        or "below the configured threshold" in joined
    ):
        return (
            "Knowledge base has no confident answer for this query; "
            "route to a human agent and consider adding a KB article "
            "for this gap."
        )

    if (
        "frustrated" in joined
        or "explicitly requested" in joined
    ):
        return (
            "Prioritize for immediate human follow-up; "
            "customer satisfaction risk is elevated."
        )

    return (
        "Review conversation context and continue "
        "troubleshooting with the customer directly."
    )


def format_handoff_json(summary: Dict[str, Any]) -> str:
    return json.dumps(
        summary,
        indent=2,
        ensure_ascii=False,
    )