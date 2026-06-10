"""
Accounts business logic.

The service layer is the single home for behaviour that both the template views
and the DRF API need. Views stay thin: they parse input, call a service, and
render the result.
"""
from __future__ import annotations

from typing import Any

from django.db import transaction

from .models import HealthHistoryEntry, Profile, User


@transaction.atomic
def register_user(
    *, email: str, password: str, full_name: str = "", role: str = User.Role.PATIENT
) -> User:
    """Create a user (and, via signal, their profile) in one transaction."""
    user = User.objects.create_user(
        email=email, password=password, full_name=full_name, role=role
    )
    return user


def update_profile(*, user: User, **fields: Any) -> Profile:
    """Patch the caller's profile with the provided fields."""
    profile = user.profile
    allowed = {
        "date_of_birth",
        "sex",
        "height_cm",
        "activity_level",
        "goal",
    }
    for key, value in fields.items():
        if key in allowed:
            setattr(profile, key, value)
    profile.save()
    return profile


def add_health_history_entry(
    *, user: User, kind: str, summary: str, details: str = "", recorded_on=None
) -> HealthHistoryEntry:
    """Append an entry to the user's health history timeline."""
    return HealthHistoryEntry.objects.create(
        user=user,
        kind=kind,
        summary=summary,
        details=details,
        recorded_on=recorded_on,
    )
