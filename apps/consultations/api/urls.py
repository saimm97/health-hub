from __future__ import annotations

from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, DoctorViewSet

router = DefaultRouter()
router.register("doctors", DoctorViewSet, basename="doctor")
router.register("bookings", BookingViewSet, basename="booking")

urlpatterns = router.urls
