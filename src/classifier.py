"""
Persona classification for:
 Technical Expert
 Frustrated User
 Business Executive
"""
import json
import re
from dataclasses import dataclass

from . import config
from . import llm_providers

SYSTEM_PROMPT = (
    "You are an advanced classification engine for a customer support platform. "
    "Analyze the vocabulary, tone, punctuation, and underlying intent of an incoming "
    "support message and classify it into exactly ONE of three personas:\n"
    "1. 'Technical Expert' - uses technical jargon, mentions APIs/logs/configs/error codes, "
    "wants precise, detailed, root-cause-level answers.\n"
    "2. 'Frustrated User' - uses emotional or urgent language, exclamation marks, words like "
    "'still', 'again', 'nothing works', repeated complaints, wants quick reassurance and simple steps.\n"
    "3. 'Business Executive' - focused on business/operational impact, timelines, cost, ROI; "
    "prefers brief, outcome-oriented communication with minimal technical detail.\n\n"
    "Respond with STRICT JSON ONLY, no markdown fences, no commentary, in exactly this shape:\n"
    '{"persona": "<one of the three above>", "confidence": <float 0-1>, "reasoning": "<one short sentence>"}'
)

_TECH_PATTERNS = [
    r"\bapi\b", r"\berror\b", r"\bcode\b", r"\b\d{3}\b", r"\bauth\w*", r"\bconfig\w*",
    r"\blog(s)?\b", r"\bendpoint\b", r"\btoken\b", r"\bjson\b", r"\bwebhook\b", r"\bsdk\b",
    r"\bstack ?trace\b", r"\bdebug\w*", r"\bquery\b", r"\bdatabase\b", r"\bintegration\b",
    r"\bheader(s)?\b", r"\bssl\b", r"\bping\b", r"\bbearer\b", r"\boauth\b",
]
_FRUSTRATION_PATTERNS = [
    r"!{1,}", r"\bstill\b", r"\bagain\b", r"\bnothing works\b", r"\bnot working\b",
    r"\bridiculous\b", r"\bunacceptable\b", r"\bfurious\b", r"\bfed up\b", r"\bworst\b",
    r"\bcan'?t believe\b", r"\bevery time\b", r"\bso frustrat\w*", r"\bimmediately\b",
    r"\bdemand\b", r"\bplease help\b", r"\b3rd time\b|\bthird time\b",
]
_EXEC_PATTERNS = [
    r"\bbusiness impact\b", r"\boperations?\b", r"\btimeline\b", r"\broi\b", r"\brevenue\b",
    r"\bcost\b", r"\bdowntime\b", r"\bsla\b", r"\bcontract\b", r"\bstakeholder(s)?\b",
    r"\bwhen will\b", r"\bresolution time\b", r"\benterprise\b", r"\bteam\b.*\bimpact\b",
    r"\baccount manager\b", r"\bescalat\w* to leadership\b",
]


@dataclass
class PersonaResult:
    persona: str
    confidence: float
    reasoning: str
    method: str  # "llm" or "rule_based"


def classify_persona(message: str) -> PersonaResult:
    llm_result = _classify_with_llm(message)
    if llm_result is not None:
        return llm_result
    return _classify_with_rules(message)


def _classify_with_llm(message: str) -> PersonaResult:
    if llm_providers.active_provider() == "offline":
        return None
    raw = llm_providers.chat(SYSTEM_PROMPT, message, temperature=0.1, max_tokens=200, json_mode=True)
    if raw == llm_providers._OFFLINE_SENTINEL:
        return None
    try:
        cleaned = raw.strip().strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()
        data = json.loads(cleaned)
        persona = data.get("persona")
        if persona not in config.PERSONAS:
            return None
        return PersonaResult(
            persona=persona,
            confidence=float(data.get("confidence", 0.7)),
            reasoning=data.get("reasoning", ""),
            method="llm",
        )
    except (json.JSONDecodeError, ValueError, TypeError):
        return None


def _classify_with_rules(message: str) -> PersonaResult:
    text = message.lower()

    def score(patterns):
        return sum(1 for p in patterns if re.search(p, text))

    tech_score = score(_TECH_PATTERNS)
    frustration_score = score(_FRUSTRATION_PATTERNS)
    exec_score = score(_EXEC_PATTERNS)

    # Caps-lock ratio is a mild additional frustration signal.
    letters = [c for c in message if c.isalpha()]
    if letters:
        caps_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
        if caps_ratio > 0.3 and len(letters) > 6:
            frustration_score += 1

    scores = {
        "Technical Expert": tech_score,
        "Frustrated User": frustration_score,
        "Business Executive": exec_score,
    }
    best_persona = max(scores, key=scores.get)
    best_score = scores[best_persona]
    total = sum(scores.values()) or 1

    if best_score == 0:
        # No clear signal at all -> default to the safest, most empathetic tone.
        return PersonaResult(
            persona=config.DEFAULT_PERSONA,
            confidence=0.34,
            reasoning="No strong persona signals detected; defaulting to a neutral, empathetic tone.",
            method="rule_based",
        )

    confidence = round(min(0.95, 0.4 + 0.5 * (best_score / total)), 2)
    reasoning = f"Rule-based scoring: technical={tech_score}, frustration={frustration_score}, executive={exec_score}."
    return PersonaResult(persona=best_persona, confidence=confidence, reasoning=reasoning, method="rule_based")
