from __future__ import annotations

from rest_framework import mixins, permissions, viewsets

from apps.nutrition.models import DietPlan, Food, MealLog

from .serializers import DietPlanSerializer, FoodSerializer, MealLogSerializer


class FoodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ["name"]


class _OwnedViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return self.model.objects.none()
        return self.model.objects.filter(user=self.request.user)

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)


class MealLogViewSet(_OwnedViewSet):
    model = MealLog
    serializer_class = MealLogSerializer
    filterset_fields = ["meal_type"]


class DietPlanViewSet(_OwnedViewSet):
    model = DietPlan
    serializer_class = DietPlanSerializer
