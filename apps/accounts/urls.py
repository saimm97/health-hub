"""Template (HTML) routes for the accounts app."""
from __future__ import annotations

from django.urls import path

from .views import DashboardView, LoginView, LogoutView

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]
