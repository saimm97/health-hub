"""API-level tests: registration, auth, and strict per-user data isolation."""
from __future__ import annotations

import pytest
from django.urls import reverse

from apps.accounts.models import HealthHistoryEntry


@pytest.mark.django_db
def test_registration_creates_user_and_profile(api_client):
    url = reverse("api:register")
    resp = api_client.post(
        url,
        {"email": "new@example.com", "password": "supersecret1", "full_name": "New User"},
        format="json",
    )
    assert resp.status_code == 201
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.get(email="new@example.com")
    # Profile auto-created by signal.
    assert user.profile is not None


@pytest.mark.django_db
def test_me_endpoint_requires_authentication(api_client):
    resp = api_client.get(reverse("api:me"))
    assert resp.status_code == 401


@pytest.mark.django_db
def test_users_only_see_their_own_health_history(auth_client, patient, make_user):
    # An entry belonging to someone else must never appear.
    other = make_user(email="someone@example.com")
    HealthHistoryEntry.objects.create(user=other, kind="note", summary="not yours")
    HealthHistoryEntry.objects.create(user=patient, kind="note", summary="mine")

    resp = auth_client.get(reverse("api:health-history-list"))
    assert resp.status_code == 200
    summaries = [e["summary"] for e in resp.json()["results"]]
    assert summaries == ["mine"]
