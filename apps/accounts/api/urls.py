"""API routes for the accounts app (mounted under /api/v1/accounts/)."""
from __future__ import annotations

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import HealthHistoryViewSet, MeView, ProfileView, RegisterView

router = DefaultRouter()
router.register("health-history", HealthHistoryViewSet, basename="health-history")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("", include(router.urls)),
]
