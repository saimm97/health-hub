"""Booking behaviour: slot reservation, double-booking, and status transitions."""
from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.consultations.models import AvailabilitySlot, Booking, DoctorProfile
from apps.consultations.services import book_slot, post_message, transition_booking


@pytest.fixture
def doctor(make_user):
    user = make_user(email="doc@example.com", role="doctor", full_name="Dr. Strange")
    return DoctorProfile.objects.create(user=user, specialty="Physiotherapy")


@pytest.fixture
def slot(doctor):
    start = timezone.now() + timedelta(days=1)
    return AvailabilitySlot.objects.create(
        doctor=doctor, starts_at=start, ends_at=start + timedelta(minutes=30)
    )


@pytest.mark.django_db
def test_booking_a_slot_marks_it_taken(patient, slot):
    booking = book_slot(patient=patient, slot_id=slot.pk, reason="knee pain follow-up")
    slot.refresh_from_db()
    assert slot.is_booked is True
    assert booking.status == Booking.Status.REQUESTED


@pytest.mark.django_db
def test_double_booking_is_rejected(patient, make_user, slot):
    book_slot(patient=patient, slot_id=slot.pk)
    other = make_user(email="other@example.com")
    with pytest.raises(ValidationError):
        book_slot(patient=other, slot_id=slot.pk)


@pytest.mark.django_db
def test_cancelling_frees_the_slot(patient, slot):
    booking = book_slot(patient=patient, slot_id=slot.pk)
    transition_booking(booking=booking, to_status=Booking.Status.CANCELLED)
    slot.refresh_from_db()
    assert slot.is_booked is False


@pytest.mark.django_db
def test_invalid_status_transition_is_blocked(patient, slot):
    booking = book_slot(patient=patient, slot_id=slot.pk)
    # requested -> completed is not allowed (must be confirmed first).
    with pytest.raises(ValidationError):
        transition_booking(booking=booking, to_status=Booking.Status.COMPLETED)


@pytest.mark.django_db
def test_outsider_cannot_message_a_booking(patient, make_user, slot):
    booking = book_slot(patient=patient, slot_id=slot.pk)
    outsider = make_user(email="nosy@example.com")
    with pytest.raises(ValidationError):
        post_message(booking=booking, sender=outsider, body="hello?")
