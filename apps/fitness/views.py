"""Server-rendered fitness pages: log workouts & readings, see recent activity."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import View

from .models import Exercise, HealthReading
from .services import log_workout, record_reading, weekly_summary


class FitnessHomeView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        return render(
            request,
            "fitness/home.html",
            {
                "summary": weekly_summary(user=user),
                "exercises": Exercise.objects.all(),
                "metrics": HealthReading.Metric.choices,
                "recent_workouts": user.workout_logs.select_related("exercise")[:8],
                "recent_readings": user.readings.all()[:8],
            },
        )


class LogWorkoutView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            log_workout(
                user=request.user,
                exercise_id=int(request.POST["exercise"]),
                sets=int(request.POST.get("sets") or 0),
                reps=int(request.POST.get("reps") or 0),
                weight_kg=request.POST.get("weight_kg") or None,
            )
            messages.success(request, "Workout logged.")
        except (KeyError, ValueError):
            messages.error(request, "Could not log that workout — check the fields.")
        return redirect("fitness:home")


class LogReadingView(LoginRequiredMixin, View):
    def post(self, request):
        try:
            record_reading(
                user=request.user,
                metric=request.POST["metric"],
                value=request.POST["value"],
            )
            messages.success(request, "Reading saved.")
        except (KeyError, ValueError):
            messages.error(request, "Could not save that reading.")
        return redirect("fitness:home")
