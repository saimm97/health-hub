"""The safety guardrail is the core of the responsible-AI story — test it hard."""
from __future__ import annotations

import pytest

from apps.coach.services import guardrail
from apps.coach.services.guardrail import Decision


@pytest.mark.parametrize(
    "message",
    [
        "What's a good push day routine?",
        "How much protein should I eat to build muscle?",
        "Can you suggest a beginner running plan?",
    ],
)
def test_normal_fitness_questions_are_allowed(message):
    assert guardrail.classify(message).decision is Decision.ALLOW


@pytest.mark.parametrize(
    "message",
    [
        "I think this mole might be cancer, what should I do?",
        "Can you diagnose my symptoms?",
        "What dosage of this medication should I take?",
    ],
)
def test_medical_questions_are_redirected_to_a_doctor(message):
    result = guardrail.classify(message)
    assert result.decision is Decision.REDIRECT_DOCTOR
    assert result.is_blocked


def test_emergencies_are_flagged_before_anything_else():
    result = guardrail.classify("I have severe chest pain and can't breathe")
    assert result.decision is Decision.EMERGENCY


def test_crisis_language_takes_priority_over_medical():
    # Contains both crisis and medical cues — crisis must win.
    result = guardrail.classify("I want to die, should I stop my medication?")
    assert result.decision is Decision.CRISIS


def test_every_blocking_decision_has_a_safe_reply():
    for decision in (Decision.EMERGENCY, Decision.CRISIS, Decision.REDIRECT_DOCTOR):
        assert decision in guardrail.SAFE_REPLIES
        assert guardrail.SAFE_REPLIES[decision]
