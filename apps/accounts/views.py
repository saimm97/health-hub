"""
Server-rendered (template) views for the accounts app.

These are intentionally thin — they call the same service layer the API uses.
Styling/templates come in the design phase; for now they render minimal pages.
"""
from __future__ import annotations

from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from .forms import RegistrationForm


class LoginView(auth_views.LoginView):
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class RegisterView(CreateView):
    """Self-service signup; logs the new user in on success."""

    form_class = RegistrationForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:dashboard")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("accounts:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    """Landing page after login — placeholder until the design phase."""

    template_name = "accounts/dashboard.html"

    def get_context_data(self, **kwargs):
        from apps.fitness.services import weekly_summary

        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["profile"] = user.profile
        ctx["history"] = user.health_history.all()[:5]
        ctx["summary"] = weekly_summary(user=user)
        ctx["recent_readings"] = user.readings.all()[:5]
        return ctx
