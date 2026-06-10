"""
Coach orchestrator — ties the pipeline together:

    user message ──▶ guardrail ──▶ (blocked? safe reply)
                                └▶ prompt builder ──▶ LLM provider ──▶ reply

Everything is persisted (including blocked turns) for an auditable history.
"""
from __future__ import annotations

from django.db import transaction

from apps.accounts.models import User
from apps.coach.models import Conversation, Message

from . import guardrail, prompts
from .providers import get_provider

# How many prior turns to include as context.
_HISTORY_LIMIT = 10


def _history_payload(conversation: Conversation) -> list[dict]:
    turns = (
        conversation.messages.filter(role__in=[Message.Role.USER, Message.Role.ASSISTANT])
        .exclude(was_blocked=True)
        .order_by("-created")[:_HISTORY_LIMIT]
    )
    # Re-order oldest-first for the model.
    return [{"role": m.role, "content": m.content} for m in reversed(list(turns))]


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

    # 3. Build a grounded prompt and call the provider.
    history = _history_payload(conversation)
    messages = prompts.build_messages(user, history, text)
    reply_text = get_provider().complete(messages)

    # 4. Persist and return the assistant's reply.
    return Message.objects.create(
        conversation=conversation, role=Message.Role.ASSISTANT, content=reply_text
    )


def start_conversation(*, user: User, title: str = "") -> Conversation:
    return Conversation.objects.create(user=user, title=title)
