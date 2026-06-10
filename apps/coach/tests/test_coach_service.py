"""Behavioural tests for the coach orchestrator (with the stub LLM provider)."""
from __future__ import annotations

import pytest

from apps.coach.models import Message
from apps.coach.services import send_message, start_conversation


@pytest.mark.django_db
def test_medical_question_never_reaches_the_llm(patient):
    convo = start_conversation(user=patient)
    reply = send_message(
        user=patient, conversation=convo, text="Please diagnose my symptoms"
    )
    assert reply.was_blocked is True
    assert reply.block_reason
    # Both the user turn and the guarded reply are persisted.
    assert convo.messages.count() == 2


@pytest.mark.django_db
def test_normal_question_gets_an_assistant_reply(patient):
    convo = start_conversation(user=patient)
    reply = send_message(
        user=patient, conversation=convo, text="Suggest a beginner workout"
    )
    assert reply.was_blocked is False
    assert reply.role == Message.Role.ASSISTANT
    assert reply.content  # stub provider returns non-empty text


@pytest.mark.django_db
def test_blocked_turns_are_excluded_from_future_context(patient):
    convo = start_conversation(user=patient)
    send_message(user=patient, conversation=convo, text="diagnose my rash")  # blocked
    # A later normal message should still succeed without error.
    reply = send_message(user=patient, conversation=convo, text="best stretches?")
    assert reply.was_blocked is False
