"""Nutrition domain: a food library, meal logging, and (AI-)generated diet plans."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel


class Food(TimeStampedModel):
    """A food item with per-100g macros (shared library)."""

    name = models.CharField(max_length=120, unique=True)
    calories_per_100g = models.PositiveSmallIntegerField()
    protein_g = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    carbs_g = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    fat_g = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta(TimeStampedModel.Meta):
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class MealLog(TimeStampedModel):
    """A meal a user ate, with the portion in grams."""

    class MealType(models.TextChoices):
        BREAKFAST = "breakfast", _("Breakfast")
        LUNCH = "lunch", _("Lunch")
        DINNER = "dinner", _("Dinner")
        SNACK = "snack", _("Snack")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meal_logs"
    )
    food = models.ForeignKey(Food, on_delete=models.PROTECT)
    meal_type = models.CharField(max_length=12, choices=MealType.choices)
    grams = models.PositiveSmallIntegerField()
    eaten_at = models.DateTimeField(db_index=True)

    class Meta(TimeStampedModel.Meta):
        ordering = ["-eaten_at"]

    @property
    def calories(self) -> float:
        return float(self.food.calories_per_100g) * self.grams / 100

    def __str__(self) -> str:
        return f"{self.user.email}: {self.food.name} ({self.grams}g)"


class DietPlan(TimeStampedModel):
    """A structured diet plan; ``is_ai_generated`` flags coach-produced plans."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="diet_plans"
    )
    name = models.CharField(max_length=120)
    daily_calorie_target = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    is_ai_generated = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name
