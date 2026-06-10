from __future__ import annotations

from rest_framework import permissions, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveAPIView

from apps.billing.models import Plan, Subscription

from .serializers import PlanSerializer, SubscriptionSerializer


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """Public list of available subscription plans."""

    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [permissions.IsAuthenticated]


class MySubscriptionView(RetrieveAPIView):
    """The caller's current subscription, if any."""

    serializer_class = SubscriptionSerializer

    def get_object(self) -> Subscription:
        sub = Subscription.objects.filter(user=self.request.user).select_related("plan").first()
        if sub is None:
            raise NotFound("No active subscription.")
        return sub
