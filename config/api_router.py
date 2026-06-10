"""
Top-level API router for ``/api/v1/``.

Each app contributes its own routes via ``apps/<app>/api/urls.py``; this module
just stitches them together so the versioned API surface lives in one place.
"""
from __future__ import annotations

from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("accounts/", include("apps.accounts.api.urls")),
    path("fitness/", include("apps.fitness.api.urls")),
    path("nutrition/", include("apps.nutrition.api.urls")),
    path("coach/", include("apps.coach.api.urls")),
    path("consultations/", include("apps.consultations.api.urls")),
    path("billing/", include("apps.billing.api.urls")),
]
