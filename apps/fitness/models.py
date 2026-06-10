"""
Fitness domain models: the exercise/routine library, workout logs, and the
health readings (weight, blood pressure, heart rate, …) that feed the coach.
"""
from __future__ import annotations

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


class Exercise(TimeStampedModel):
    """A reusable exercise in the shared library (seeded, not per-user)."""

    class Muscle(models.TextChoices):
        CHEST = "chest", _("Chest")
        BACK = "back", _("Back")
        LEGS = "legs", _("Legs")
        SHOULDERS = "shoulders", _("Shoulders")
        ARMS = "arms", _("Arms")
        CORE = "core", _("Core")
        CARDIO = "cardio", _("Cardio")
        FULL_BODY = "full_body", _("Full body")

    name = models.CharField(max_length=120, unique=True)
    muscle_group = models.CharField(max_length=16, choices=Muscle.choices)
    equipment = models.CharField(max_length=120, blank=True)
    instructions = models.TextField(blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Routine(TimeStampedModel):
    """A named workout plan. Library routines have ``owner=None``; users can
    also create or be assigned personalised ones (incl. AI-generated)."""

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="routines",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    is_ai_generated = models.BooleanField(default=False)
    exercises = models.ManyToManyField(Exercise, through="RoutineItem", related_name="routines")

    def __str__(self) -> str:
        return self.name


class RoutineItem(TimeStampedModel):
    """One exercise within a routine, with prescribed sets/reps."""

    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name="items")
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    order = models.PositiveSmallIntegerField(default=0)
    sets = models.PositiveSmallIntegerField(default=3)
    reps = models.PositiveSmallIntegerField(default=10)

    class Meta(TimeStampedModel.Meta):
        ordering = ["order"]
        unique_together = [("routine", "exercise")]

    def __str__(self) -> str:
        return f"{self.exercise.name} ({self.sets}x{self.reps})"


class WorkoutLog(TimeStampedModel):
    """A record that a user performed an exercise — the raw progress data."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workout_logs"
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.PROTECT)
    performed_at = models.DateTimeField(db_index=True)
    sets = models.PositiveSmallIntegerField(default=0)
    reps = models.PositiveSmallIntegerField(default=0)
    weight_kg = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0)],
    )
    notes = models.CharField(max_length=255, blank=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["-performed_at"]

    def __str__(self) -> str:
        return f"{self.user.email} · {self.exercise.name} @ {self.performed_at:%Y-%m-%d}"


class HealthReading(TimeStampedModel):
    """A time-stamped vital sign or body metric."""

    class Metric(models.TextChoices):
        WEIGHT = "weight_kg", _("Weight (kg)")
        HEART_RATE = "heart_rate_bpm", _("Resting heart rate (bpm)")
        SYSTOLIC = "bp_systolic", _("Blood pressure — systolic")
        DIASTOLIC = "bp_diastolic", _("Blood pressure — diastolic")
        SLEEP_HOURS = "sleep_hours", _("Sleep (hours)")
        STEPS = "steps", _("Steps")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="readings"
    )
    metric = models.CharField(max_length=20, choices=Metric.choices, db_index=True)
    value = models.DecimalField(max_digits=8, decimal_places=2)
    recorded_at = models.DateTimeField(db_index=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["-recorded_at"]
        indexes = [models.Index(fields=["user", "metric", "recorded_at"])]

    def __str__(self) -> str:
        return f"{self.get_metric_display()}={self.value} ({self.user.email})"
