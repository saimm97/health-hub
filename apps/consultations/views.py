"""Server-rendered consultation pages: browse doctors, book a slot, see bookings."""
from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from .models import AvailabilitySlot, Booking, DoctorProfile
from .services import book_slot


class DoctorListView(LoginRequiredMixin, View):
    def get(self, request):
        doctors = DoctorProfile.objects.filter(is_accepting=True).select_related("user")
        return render(request, "consultations/doctor_list.html", {"doctors": doctors})


class DoctorDetailView(LoginRequiredMixin, View):
    def get(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, pk=pk)
        slots = AvailabilitySlot.objects.filter(doctor=doctor, is_booked=False)
        return render(
            request,
            "consultations/doctor_detail.html",
            {"doctor": doctor, "slots": slots},
        )


class BookSlotView(LoginRequiredMixin, View):
    def post(self, request, slot_id):
        try:
            book_slot(
                patient=request.user,
                slot_id=int(slot_id),
                reason=request.POST.get("reason", ""),
            )
            messages.success(request, "Consultation requested.")
        except ValidationError as exc:
            messages.error(request, exc.messages[0])
        return redirect("consultations:my_bookings")


class MyBookingsView(LoginRequiredMixin, View):
    def get(self, request):
        bookings = (
            Booking.objects.filter(Q(patient=request.user) | Q(doctor__user=request.user))
            .select_related("doctor__user", "slot")
        )
        return render(request, "consultations/my_bookings.html", {"bookings": bookings})
