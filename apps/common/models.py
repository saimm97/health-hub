"""Reusable abstract models shared across apps."""
from __future__ import annotations

import uuid

from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base that adds self-updating ``created`` / ``modified`` fields."""

    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created"]


class UUIDTimeStampedModel(TimeStampedModel):
    """Like :class:`TimeStampedModel` but with a non-guessable UUID primary key.

    Useful for resources exposed in URLs/APIs where sequential integer ids
    would leak volume or allow enumeration (bookings, payments, etc.).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta(TimeStampedModel.Meta):
        abstract = True
