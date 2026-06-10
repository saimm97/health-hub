from __future__ import annotations

from django.urls import path

from .views import BookSlotView, DoctorDetailView, DoctorListView, MyBookingsView

app_name = "consultations"

urlpatterns = [
    path("", DoctorListView.as_view(), name="doctor_list"),
    path("doctor/<int:pk>/", DoctorDetailView.as_view(), name="doctor_detail"),
    path("slots/<int:slot_id>/book/", BookSlotView.as_view(), name="book_slot"),
    path("my-bookings/", MyBookingsView.as_view(), name="my_bookings"),
]
