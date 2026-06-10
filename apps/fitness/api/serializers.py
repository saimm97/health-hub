from __future__ import annotations

from rest_framework import serializers

from apps.fitness.models import Exercise, HealthReading, Routine, RoutineItem, WorkoutLog


class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ["id", "name", "muscle_group", "equipment", "instructions"]


class RoutineItemSerializer(serializers.ModelSerializer):
    exercise_name = serializers.CharField(source="exercise.name", read_only=True)

    class Meta:
        model = RoutineItem
        fields = ["id", "exercise", "exercise_name", "order", "sets", "reps"]


class RoutineSerializer(serializers.ModelSerializer):
    items = RoutineItemSerializer(many=True, read_only=True)

    class Meta:
        model = Routine
        fields = ["id", "name", "description", "is_ai_generated", "items"]


class WorkoutLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkoutLog
        fields = ["id", "exercise", "performed_at", "sets", "reps", "weight_kg", "notes"]
        read_only_fields = ["id"]


class HealthReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthReading
        fields = ["id", "metric", "value", "recorded_at"]
        read_only_fields = ["id"]
