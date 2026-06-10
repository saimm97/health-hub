"""DRF views for the accounts app."""
from __future__ import annotations

from rest_framework import generics, permissions, viewsets

from apps.accounts.models import HealthHistoryEntry
from apps.accounts.services import update_profile

from .serializers import (
    HealthHistoryEntrySerializer,
    ProfileSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    """Public endpoint to create a patient account."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    """Return the authenticated user with their nested profile."""

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ProfileView(generics.RetrieveUpdateAPIView):
    """Read or update the caller's own profile."""

    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user.profile

    def perform_update(self, serializer) -> None:
        update_profile(user=self.request.user, **serializer.validated_data)


class HealthHistoryViewSet(viewsets.ModelViewSet):
    """CRUD over the caller's own health-history timeline."""

    serializer_class = HealthHistoryEntrySerializer

    def get_queryset(self):
        # Users only ever see their own entries.
        return HealthHistoryEntry.objects.filter(user=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)
