"""Fitness business logic and the read-side queries the coach depends on."""
from __future__ import annotations

from datetime import timedelta

from django.db.models import Avg, Count, Max
from django.utils import timezone

from apps.accounts.models import User

from .models import HealthReading, WorkoutLog


def log_workout(
    *, user: User, exercise_id: int, performed_at=None, sets: int = 0, reps: int = 0,
    weight_kg=None, notes: str = "",
) -> WorkoutLog:
    return WorkoutLog.objects.create(
        user=user,
        exercise_id=exercise_id,
        performed_at=performed_at or timezone.now(),
        sets=sets,
        reps=reps,
        weight_kg=weight_kg,
        notes=notes,
    )


def record_reading(*, user: User, metric: str, value, recorded_at=None) -> HealthReading:
    return HealthReading.objects.create(
        user=user,
        metric=metric,
        value=value,
        recorded_at=recorded_at or timezone.now(),
    )


def weekly_summary(*, user: User) -> dict:
    """Aggregate the last 7 days of activity — used by the dashboard and the
    AI coach's prompt builder, so the model reasons over real data."""
    since = timezone.now() - timedelta(days=7)
    workouts = WorkoutLog.objects.filter(user=user, performed_at__gte=since)
    latest_weight = (
        HealthReading.objects.filter(user=user, metric=HealthReading.Metric.WEIGHT)
        .order_by("-recorded_at")
        .values_list("value", flat=True)
        .first()
    )
    agg = workouts.aggregate(
        sessions=Count("id"),
        last_workout=Max("performed_at"),
        avg_reps=Avg("reps"),
    )
    return {
        "workout_sessions": agg["sessions"],
        "last_workout": agg["last_workout"],
        "avg_reps": float(agg["avg_reps"]) if agg["avg_reps"] is not None else None,
        "latest_weight_kg": float(latest_weight) if latest_weight is not None else None,
    }
