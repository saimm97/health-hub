from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import DietPlanViewSet, FoodViewSet, MealLogViewSet

router = DefaultRouter()
router.register("foods", FoodViewSet, basename="food")
router.register("meal-logs", MealLogViewSet, basename="meal-log")
router.register("diet-plans", DietPlanViewSet, basename="diet-plan")

urlpatterns = router.urls
