"""
Safety guardrail — the first thing every user message passes through.

The coach is a *fitness & wellness* assistant, not a medical one. This layer
classifies incoming messages and blocks anything that strays into medical
diagnosis, emergencies, or mental-health crisis, redirecting the user to a real
professional instead of letting the LLM answer.

The implementation here is a transparent, auditable rule set. It is deliberately
behind a single ``classify()`` function so it can later be swapped for (or
combined with) an ML classifier without touching the rest of the pipeline.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum


class Decision(StrEnum):
    ALLOW = "allow"
    REDIRECT_DOCTOR = "redirect_doctor"
    EMERGENCY = "emergency"
    CRISIS = "crisis"


@dataclass(frozen=True)
class GuardrailResult:
    decision: Decision
    reason: str

    @property
    def is_blocked(self) -> bool:
        return self.decision is not Decision.ALLOW


# --- Pattern sets (word-boundary matched, case-insensitive) -----------------

_EMERGENCY = [
    r"chest pain", r"can'?t breathe", r"shortness of breath", r"stroke",
    r"heart attack", r"unconscious", r"severe bleeding", r"overdose",
]

_CRISIS = [
    r"suicid", r"kill myself", r"end my life", r"self[- ]harm", r"want to die",
]

_MEDICAL = [
    r"\bdiagnos", r"\bsymptom", r"\bprescri", r"\bmedication\b", r"\bdosage\b",
    r"\bcancer\b", r"\btumou?r\b", r"\binfection\b", r"\bantibiotic", r"\brash\b",
    r"\bmole\b", r"is this normal\b", r"should i (stop|take|see a doctor)",
    r"\bblood pressure\b.*\b(high|low|dangerous)\b", r"\bdiabet",
]

_EMERGENCY_RE = re.compile("|".join(_EMERGENCY), re.IGNORECASE)
_CRISIS_RE = re.compile("|".join(_CRISIS), re.IGNORECASE)
_MEDICAL_RE = re.compile("|".join(_MEDICAL), re.IGNORECASE)


def classify(message: str) -> GuardrailResult:
    """Return a guardrail decision for a user message.

    Order matters: crisis and emergency checks come before the general medical
    check so the most urgent redirect always wins.
    """
    text = message.strip()

    if _CRISIS_RE.search(text):
        return GuardrailResult(
            Decision.CRISIS,
            "Message indicates a possible mental-health crisis.",
        )
    if _EMERGENCY_RE.search(text):
        return GuardrailResult(
            Decision.EMERGENCY,
            "Message describes a possible medical emergency.",
        )
    if _MEDICAL_RE.search(text):
        return GuardrailResult(
            Decision.REDIRECT_DOCTOR,
            "Message asks for medical advice outside the coach's scope.",
        )
    return GuardrailResult(Decision.ALLOW, "")


# Canned safe replies shown instead of an LLM answer when blocked.
SAFE_REPLIES = {
    Decision.EMERGENCY: (
        "This sounds like it could be a medical emergency. Please contact your "
        "local emergency services right now — I'm a fitness coach and can't help "
        "with urgent medical situations."
    ),
    Decision.CRISIS: (
        "I'm really sorry you're feeling this way. I'm not able to help with this, "
        "but please reach out to a crisis line or a mental-health professional "
        "right away — you deserve real support from someone qualified to give it."
    ),
    Decision.REDIRECT_DOCTOR: (
        "That's a medical question and outside what I can safely advise on as a "
        "fitness & wellness coach. The best next step is to book a consultation "
        "with a doctor through HealthHub, who can give you proper guidance."
    ),
}
