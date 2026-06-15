"""
Coach orchestrator.

    user message ──▶ guardrail ──▶ (blocked? safe reply)
                                └▶ [ your LLM integration goes here ]

The guardrail and persistence are in place; the actual LLM call is intentionally
NOT implemented — wire in your own provider where marked below.

Everything is persisted (including blocked turns) for an auditable history.
"""
from __future__ import annotations

from django.db import transaction

from apps.accounts.models import User
from apps.coach.models import Conversation, Message

from . import guardrail

# Shown until an LLM provider is integrated (see TODO in ``send_message``).
_NOT_CONFIGURED_REPLY = (
    "The AI coach isn't connected to a language model yet. "
    "Integrate your LLM provider in apps/coach/services/coach.py."
)


@transaction.atomic
def send_message(*, user: User, conversation: Conversation, text: str) -> Message:
    """Process one user turn and return the assistant's reply message.

    The conversation must belong to ``user`` (callers enforce ownership).
    """
    # 1. Persist the user's turn.
    Message.objects.create(
        conversation=conversation, role=Message.Role.USER, content=text
    )

    # 2. Guardrail — runs before any LLM call.
    verdict = guardrail.classify(text)
    if verdict.is_blocked:
        reply = guardrail.SAFE_REPLIES[verdict.decision]
        return Message.objects.create(
            conversation=conversation,
            role=Message.Role.ASSISTANT,
            content=reply,
            was_blocked=True,
            block_reason=verdict.reason,
        )

    # 3. TODO: integrate your LLM provider here.
    #    Build your prompt/context from `user` and the conversation history,
    #    call your model, and use its response as `reply_text`.
    reply_text = _NOT_CONFIGURED_REPLY

    # 4. Persist and return the assistant's reply.
    return Message.objects.create(
        conversation=conversation, role=Message.Role.ASSISTANT, content=reply_text
    )


def start_conversation(*, user: User, title: str = "") -> Conversation:
    return Conversation.objects.create(user=user, title=title)
