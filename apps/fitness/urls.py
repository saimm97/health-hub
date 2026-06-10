from __future__ import annotations

from django.urls import path

from .views import FitnessHomeView, LogReadingView, LogWorkoutView

app_name = "fitness"

urlpatterns = [
    path("", FitnessHomeView.as_view(), name="home"),
    path("log-workout/", LogWorkoutView.as_view(), name="log_workout"),
    path("log-reading/", LogReadingView.as_view(), name="log_reading"),
]
