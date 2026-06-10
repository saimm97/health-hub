"""
Consultations domain: doctor profiles, their availability, patient bookings,
and a per-booking message thread.

This is the telemedicine *infrastructure* — built end to end. Real licensed
doctors, video, and payments are deliberately out of Phase 1 (see README
roadmap); doctor accounts are seeded for demos.
"""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel, UUIDTimeStampedModel


class DoctorProfile(TimeStampedModel):
    """Extends a ``role=doctor`` user with professional details."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        limit_choices_to={"role": "doctor"},
    )
    specialty = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    years_experience = models.PositiveSmallIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_accepting = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"Dr. {self.user.full_name or self.user.email} ({self.specialty})"


class AvailabilitySlot(TimeStampedModel):
    """A bookable time window offered by a doctor."""

    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="slots"
    )
    starts_at = models.DateTimeField(db_index=True)
    ends_at = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    class Meta(TimeStampedModel.Meta):
        ordering = ["starts_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["doctor", "starts_at"], name="unique_doctor_slot_start"
            )
        ]

    def __str__(self) -> str:
        return f"{self.doctor} @ {self.starts_at:%Y-%m-%d %H:%M}"


class Booking(UUIDTimeStampedModel):
    """A patient's request to consult a doctor in a given slot."""

    class Status(models.TextChoices):
        REQUESTED = "requested", _("Requested")
        CONFIRMED = "confirmed", _("Confirmed")
        COMPLETED = "completed", _("Completed")
        CANCELLED = "cancelled", _("Cancelled")

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.PROTECT, related_name="bookings"
    )
    slot = models.OneToOneField(
        AvailabilitySlot, on_delete=models.PROTECT, related_name="booking"
    )
    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.REQUESTED, db_index=True
    )
    reason = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"Booking<{self.patient.email} → {self.doctor}>"


class ConsultationMessage(TimeStampedModel):
    """A message within a booking's thread (patient ↔ doctor)."""

    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="messages"
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()

    class Meta(TimeStampedModel.Meta):
        ordering = ["created"]

    def __str__(self) -> str:
        return f"{self.sender.email}: {self.body[:40]}"
