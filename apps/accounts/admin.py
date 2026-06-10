"""Admin registrations for the accounts app."""
from __future__ import annotations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import HealthHistoryEntry, Profile, User


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin tuned for the email-based custom user model."""

    inlines = [ProfileInline]
    ordering = ["email"]
    list_display = ["email", "full_name", "role", "is_staff", "is_active"]
    list_filter = ["role", "is_staff", "is_active"]
    search_fields = ["email", "full_name"]
    readonly_fields = ["created", "modified", "last_login"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal", {"fields": ("full_name", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "created", "modified")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(HealthHistoryEntry)
class HealthHistoryEntryAdmin(admin.ModelAdmin):
    list_display = ["user", "kind", "summary", "recorded_on", "created"]
    list_filter = ["kind"]
    search_fields = ["user__email", "summary", "details"]
