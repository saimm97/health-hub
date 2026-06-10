from __future__ import annotations

from django.db.models import Q
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from apps.consultations.models import AvailabilitySlot, Booking, DoctorProfile
from apps.consultations.services import (
    SlotUnavailable,
    book_slot,
    post_message,
    transition_booking,
)

from .serializers import (
    AvailabilitySlotSerializer,
    BookingSerializer,
    ConsultationMessageSerializer,
    DoctorProfileSerializer,
)


class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    """Public directory of doctors and their open slots."""

    queryset = DoctorProfile.objects.filter(is_accepting=True).select_related("user")
    serializer_class = DoctorProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["specialty"]
    search_fields = ["specialty", "user__full_name"]

    @action(detail=True, methods=["get"])
    def slots(self, request, pk=None):
        slots = AvailabilitySlot.objects.filter(doctor_id=pk, is_booked=False)
        return Response(AvailabilitySlotSerializer(slots, many=True).data)


class BookingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """A patient's bookings (and, for doctors, bookings made with them)."""

    serializer_class = BookingSerializer

    def get_queryset(self):
        user = self.request.user
        return Booking.objects.filter(
            Q(patient=user) | Q(doctor__user=user)
        ).select_related("doctor__user", "slot")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            booking = book_slot(
                patient=request.user,
                slot_id=serializer.validated_data["slot"].pk,
                reason=serializer.validated_data.get("reason", ""),
            )
        except SlotUnavailable as exc:
            raise DRFValidationError({"slot": exc.messages}) from exc
        return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        transition_booking(booking=booking, to_status=Booking.Status.CANCELLED)
        return Response(self.get_serializer(booking).data)

    @action(detail=True, methods=["get", "post"], serializer_class=ConsultationMessageSerializer)
    def messages(self, request, pk=None):
        booking = self.get_object()
        if request.method == "POST":
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            msg = post_message(
                booking=booking, sender=request.user, body=serializer.validated_data["body"]
            )
            return Response(self.get_serializer(msg).data, status=status.HTTP_201_CREATED)
        data = ConsultationMessageSerializer(booking.messages.all(), many=True).data
        return Response(data)
