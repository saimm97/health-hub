"""
AI coach domain models: conversations and their messages.

Every assistant message records whether the safety guardrail intervened, so the
behaviour is auditable — important for anything touching health.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


class Conversation(TimeStampedModel):
    """A coaching chat thread belonging to one user."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations"
    )
    title = models.CharField(max_length=140, blank=True)

    def __str__(self) -> str:
        return self.title or f"Conversation #{self.pk}"


class Message(TimeStampedModel):
    """A single turn in a conversation."""

    class Role(models.TextChoices):
        USER = "user", _("User")
        ASSISTANT = "assistant", _("Assistant")
        SYSTEM = "system", _("System")

    conversation = models.ForeignKey(
        Conversation, on_delete=models.CASCADE, related_name="messages"
    )
    role = models.CharField(max_length=12, choices=Role.choices)
    content = models.TextField()

    # Guardrail audit trail: set when the safety layer blocked/redirected a turn.
    was_blocked = models.BooleanField(default=False)
    block_reason = models.CharField(max_length=140, blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["created"]

    def __str__(self) -> str:
        return f"{self.role}: {self.content[:40]}"
