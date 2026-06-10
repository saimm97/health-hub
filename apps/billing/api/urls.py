from __future__ import annotations

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import MySubscriptionView, PlanViewSet

router = DefaultRouter()
router.register("plans", PlanViewSet, basename="plan")

urlpatterns = [
    path("subscription/", MySubscriptionView.as_view(), name="my-subscription"),
    *router.urls,
]
