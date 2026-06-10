from __future__ import annotations

from rest_framework import serializers

from apps.billing.models import Plan, Subscription


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ["id", "name", "price_cents", "currency", "interval", "is_active"]


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)

    class Meta:
        model = Subscription
        fields = ["id", "plan", "status", "current_period_end"]
        read_only_fields = fields
