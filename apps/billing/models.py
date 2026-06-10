"""
Billing domain — designed Stripe-ready, but the Stripe calls are wired last
(see README roadmap). Models capture the local source of truth; ``stripe_*``
fields hold the external identifiers once integration is switched on.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel, UUIDTimeStampedModel


class Plan(TimeStampedModel):
    """A subscription tier (e.g. Free, Premium coaching)."""

    name = models.CharField(max_length=80, unique=True)
    price_cents = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default="usd")
    interval = models.CharField(max_length=10, default="month")  # month | year
    stripe_price_id = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class Subscription(TimeStampedModel):
    """A user's membership of a plan."""

    class Status(models.TextChoices):
        ACTIVE = "active", _("Active")
        PAST_DUE = "past_due", _("Past due")
        CANCELLED = "cancelled", _("Cancelled")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscription"
    )
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    stripe_customer_id = models.CharField(max_length=120, blank=True)
    stripe_subscription_id = models.CharField(max_length=120, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.user.email} · {self.plan.name} ({self.status})"


class Payment(UUIDTimeStampedModel):
    """A recorded payment (subscription charge or one-off consultation fee)."""

    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        SUCCEEDED = "succeeded", _("Succeeded")
        FAILED = "failed", _("Failed")
        REFUNDED = "refunded", _("Refunded")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments"
    )
    amount_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=3, default="usd")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    description = models.CharField(max_length=255, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=120, blank=True)

    def __str__(self) -> str:
        return f"{self.user.email}: {self.amount_cents/100:.2f} {self.currency} ({self.status})"
