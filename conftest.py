"""Shared pytest fixtures."""
from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def make_user(db):
    """Factory fixture: create a user (profile is auto-created via signal)."""

    def _make(email="user@example.com", password="testpass123", **extra):
        return User.objects.create_user(email=email, password=password, **extra)

    return _make


@pytest.fixture
def patient(make_user):
    return make_user(email="patient@example.com")


@pytest.fixture
def auth_client(api_client, patient):
    api_client.force_authenticate(user=patient)
    return api_client
