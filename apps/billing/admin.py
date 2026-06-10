from __future__ import annotations

from django.contrib import admin

from .models import Payment, Plan, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price_cents", "currency", "interval", "is_active"]
    list_filter = ["is_active", "interval"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["user", "plan", "status", "current_period_end"]
    list_filter = ["status", "plan"]
    search_fields = ["user__email"]


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["user", "amount_cents", "currency", "status", "created"]
    list_filter = ["status", "currency"]
    search_fields = ["user__email", "stripe_payment_intent_id"]
