"""Behavioural tests for the coach orchestrator (guardrail + persistence)."""
from __future__ import annotations

import pytest

from apps.coach.models import Message
from apps.coach.services import send_message, start_conversation


@pytest.mark.django_db
def test_medical_question_is_blocked_by_the_guardrail(patient):
    convo = start_conversation(user=patient)
    reply = send_message(
        user=patient, conversation=convo, text="Please diagnose my symptoms"
    )
    assert reply.was_blocked is True
    assert reply.block_reason
    # Both the user turn and the guarded reply are persisted.
    assert convo.messages.count() == 2


@pytest.mark.django_db
def test_normal_question_persists_an_assistant_reply(patient):
    # No LLM is integrated, so the assistant returns the placeholder reply —
    # the point of this test is that the pipeline persists turns correctly.
    convo = start_conversation(user=patient)
    reply = send_message(
        user=patient, conversation=convo, text="Suggest a beginner workout"
    )
    assert reply.was_blocked is False
    assert reply.role == Message.Role.ASSISTANT
    assert reply.content
    assert convo.messages.count() == 2
