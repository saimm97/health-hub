from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import (
    ExerciseViewSet,
    HealthReadingViewSet,
    RoutineViewSet,
    WorkoutLogViewSet,
)

router = DefaultRouter()
router.register("exercises", ExerciseViewSet, basename="exercise")
router.register("routines", RoutineViewSet, basename="routine")
router.register("workout-logs", WorkoutLogViewSet, basename="workout-log")
router.register("readings", HealthReadingViewSet, basename="reading")

urlpatterns = router.urls
