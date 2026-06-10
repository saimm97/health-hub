from __future__ import annotations

from rest_framework import serializers

from apps.consultations.models import (
    AvailabilitySlot,
    Booking,
    ConsultationMessage,
    DoctorProfile,
)


class DoctorProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            "id", "name", "specialty", "bio", "years_experience",
            "consultation_fee", "is_accepting",
        ]


class AvailabilitySlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilitySlot
        fields = ["id", "doctor", "starts_at", "ends_at", "is_booked"]
        read_only_fields = ["id", "is_booked"]


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["id", "doctor", "slot", "status", "reason", "created"]
        read_only_fields = ["id", "doctor", "status", "created"]


class ConsultationMessageSerializer(serializers.ModelSerializer):
    sender_email = serializers.EmailField(source="sender.email", read_only=True)

    class Meta:
        model = ConsultationMessage
        fields = ["id", "sender_email", "body", "created"]
        read_only_fields = ["id", "sender_email", "created"]
