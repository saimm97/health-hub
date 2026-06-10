from __future__ import annotations

from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.fitness.models import Exercise, HealthReading, Routine, WorkoutLog
from apps.fitness.services import weekly_summary

from .serializers import (
    ExerciseSerializer,
    HealthReadingSerializer,
    RoutineSerializer,
    WorkoutLogSerializer,
)


class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """Shared, read-only exercise library (browsable by any authenticated user)."""

    queryset = Exercise.objects.all()
    serializer_class = ExerciseSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["muscle_group"]
    search_fields = ["name"]


class RoutineViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RoutineSerializer

    def get_queryset(self):
        # Library routines (owner is null) plus the caller's own routines.
        user = self.request.user
        return (
            Routine.objects.filter(owner__isnull=True)
            | Routine.objects.filter(owner=user)
        ).prefetch_related("items__exercise")


class _OwnedByUserMixin(mixins.CreateModelMixin, mixins.ListModelMixin,
                        mixins.RetrieveModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """Base for resources scoped strictly to the requesting user."""

    def get_queryset(self):
        # Schema generation introspects with an anonymous user — return an empty
        # queryset of the right model instead of blowing up.
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()
        return self.model.objects.filter(user=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)


class WorkoutLogViewSet(_OwnedByUserMixin):
    model = WorkoutLog
    serializer_class = WorkoutLogSerializer

    @action(detail=False, methods=["get"])
    def weekly_summary(self, request):
        return Response(weekly_summary(user=request.user))


class HealthReadingViewSet(_OwnedByUserMixin):
    model = HealthReading
    serializer_class = HealthReadingSerializer
    filterset_fields = ["metric"]
