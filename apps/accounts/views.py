"""
Server-rendered (template) views for the accounts app.

These are intentionally thin — they call the same service layer the API uses.
Styling/templates come in the design phase; for now they render minimal pages.
"""
from __future__ import annotations

from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("accounts:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    """Landing page after login — placeholder until the design phase."""

    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = self.request.user.profile
        ctx["history"] = self.request.user.health_history.all()[:10]
        return ctx
