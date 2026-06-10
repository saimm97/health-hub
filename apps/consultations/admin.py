from __future__ import annotations

from django.contrib import admin

from .models import AvailabilitySlot, Booking, ConsultationMessage, DoctorProfile


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ["__str__", "specialty", "years_experience", "is_accepting"]
    list_filter = ["specialty", "is_accepting"]
    search_fields = ["user__email", "user__full_name", "specialty"]


@admin.register(AvailabilitySlot)
class AvailabilitySlotAdmin(admin.ModelAdmin):
    list_display = ["doctor", "starts_at", "ends_at", "is_booked"]
    list_filter = ["is_booked"]
    date_hierarchy = "starts_at"


class ConsultationMessageInline(admin.TabularInline):
    model = ConsultationMessage
    extra = 0
    readonly_fields = ["sender", "body", "created"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["__str__", "status", "created"]
    list_filter = ["status"]
    search_fields = ["patient__email", "doctor__user__email"]
    inlines = [ConsultationMessageInline]
