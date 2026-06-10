from __future__ import annotations

from django.contrib import admin

from .models import DietPlan, Food, MealLog


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ["name", "calories_per_100g", "protein_g", "carbs_g", "fat_g"]
    search_fields = ["name"]


@admin.register(MealLog)
class MealLogAdmin(admin.ModelAdmin):
    list_display = ["user", "food", "meal_type", "grams", "eaten_at"]
    list_filter = ["meal_type"]
    search_fields = ["user__email", "food__name"]
    date_hierarchy = "eaten_at"


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "daily_calorie_target", "is_ai_generated"]
    list_filter = ["is_ai_generated"]
    search_fields = ["user__email", "name"]
