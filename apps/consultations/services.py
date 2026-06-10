"""
Consultation booking logic.

Booking a slot is the one place a race condition really bites (two patients
grabbing the same slot), so we lock the slot row inside a transaction rather
than relying on application-level checks alone.
"""
from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.accounts.models import User

from .models import AvailabilitySlot, Booking, ConsultationMessage


class SlotUnavailable(ValidationError):
    """Raised when a slot is already taken."""


@transaction.atomic
def book_slot(*, patient: User, slot_id: int, reason: str = "") -> Booking:
    """Atomically reserve a slot and create a booking.

    ``select_for_update`` locks the slot row so concurrent requests can't both
    pass the ``is_booked`` check.
    """
    slot = (
        AvailabilitySlot.objects.select_for_update()
        .select_related("doctor")
        .get(pk=slot_id)
    )
    if slot.is_booked:
        raise SlotUnavailable("That time slot has just been taken.")

    slot.is_booked = True
    slot.save(update_fields=["is_booked"])

    return Booking.objects.create(
        patient=patient,
        doctor=slot.doctor,
        slot=slot,
        reason=reason,
        status=Booking.Status.REQUESTED,
    )


_ALLOWED_TRANSITIONS = {
    Booking.Status.REQUESTED: {Booking.Status.CONFIRMED, Booking.Status.CANCELLED},
    Booking.Status.CONFIRMED: {Booking.Status.COMPLETED, Booking.Status.CANCELLED},
    Booking.Status.COMPLETED: set(),
    Booking.Status.CANCELLED: set(),
}


@transaction.atomic
def transition_booking(*, booking: Booking, to_status: str) -> Booking:
    """Move a booking through its lifecycle, enforcing valid transitions."""
    if to_status not in _ALLOWED_TRANSITIONS[booking.status]:
        raise ValidationError(
            f"Cannot move booking from {booking.status} to {to_status}."
        )
    booking.status = to_status
    booking.save(update_fields=["status"])

    # Free the slot again if the booking is cancelled.
    if to_status == Booking.Status.CANCELLED:
        AvailabilitySlot.objects.filter(pk=booking.slot_id).update(is_booked=False)

    return booking


def post_message(*, booking: Booking, sender: User, body: str) -> ConsultationMessage:
    """Add a message to a booking thread (sender must be patient or doctor)."""
    is_participant = sender == booking.patient or sender == booking.doctor.user
    if not is_participant:
        raise ValidationError("Only the booking's participants can message.")
    return ConsultationMessage.objects.create(booking=booking, sender=sender, body=body)
