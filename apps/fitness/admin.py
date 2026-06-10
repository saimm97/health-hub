from __future__ import annotations

from django.contrib import admin

from .models import Exercise, HealthReading, Routine, RoutineItem, WorkoutLog


class RoutineItemInline(admin.TabularInline):
    model = RoutineItem
    extra = 1


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ["name", "muscle_group", "equipment"]
    list_filter = ["muscle_group"]
    search_fields = ["name"]


@admin.register(Routine)
class RoutineAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "is_ai_generated", "created"]
    list_filter = ["is_ai_generated"]
    search_fields = ["name", "owner__email"]
    inlines = [RoutineItemInline]


@admin.register(WorkoutLog)
class WorkoutLogAdmin(admin.ModelAdmin):
    list_display = ["user", "exercise", "performed_at", "sets", "reps", "weight_kg"]
    list_filter = ["exercise__muscle_group"]
    search_fields = ["user__email", "exercise__name"]
    date_hierarchy = "performed_at"


@admin.register(HealthReading)
class HealthReadingAdmin(admin.ModelAdmin):
    list_display = ["user", "metric", "value", "recorded_at"]
    list_filter = ["metric"]
    search_fields = ["user__email"]
    date_hierarchy = "recorded_at"
