from __future__ import annotations

from rest_framework import serializers

from apps.nutrition.models import DietPlan, Food, MealLog


class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ["id", "name", "calories_per_100g", "protein_g", "carbs_g", "fat_g"]


class MealLogSerializer(serializers.ModelSerializer):
    calories = serializers.FloatField(read_only=True)

    class Meta:
        model = MealLog
        fields = ["id", "food", "meal_type", "grams", "eaten_at", "calories"]
        read_only_fields = ["id", "calories"]


class DietPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DietPlan
        fields = ["id", "name", "daily_calorie_target", "notes", "is_ai_generated"]
        read_only_fields = ["id", "is_ai_generated"]
