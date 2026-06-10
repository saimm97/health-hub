"""
Accounts domain models.

We use a custom ``User`` model from the very first migration (swapping it in
later is painful). Email is the login identifier and a ``role`` field drives
the patient/doctor split used across the platform.
"""
from __future__ import annotations

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import TimeStampedModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """Platform user. Login is by email; ``role`` distinguishes patients/doctors."""

    class Role(models.TextChoices):
        PATIENT = "patient", _("Patient")
        DOCTOR = "doctor", _("Doctor")
        ADMIN = "admin", _("Admin")

    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("full name"), max_length=150, blank=True)
    role = models.CharField(
        max_length=16, choices=Role.choices, default=Role.PATIENT, db_index=True
    )

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []  # email + password are prompted by default

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        return self.email

    @property
    def is_doctor(self) -> bool:
        return self.role == self.Role.DOCTOR

    @property
    def is_patient(self) -> bool:
        return self.role == self.Role.PATIENT


class Profile(TimeStampedModel):
    """Per-user health profile — the static facts the AI coach reasons over."""

    class Sex(models.TextChoices):
        MALE = "male", _("Male")
        FEMALE = "female", _("Female")
        OTHER = "other", _("Other")
        UNSPECIFIED = "unspecified", _("Prefer not to say")

    class ActivityLevel(models.TextChoices):
        SEDENTARY = "sedentary", _("Sedentary")
        LIGHT = "light", _("Lightly active")
        MODERATE = "moderate", _("Moderately active")
        ACTIVE = "active", _("Active")
        ATHLETE = "athlete", _("Very active / athlete")

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    date_of_birth = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=12, choices=Sex.choices, default=Sex.UNSPECIFIED)
    height_cm = models.PositiveSmallIntegerField(null=True, blank=True)
    activity_level = models.CharField(
        max_length=12, choices=ActivityLevel.choices, default=ActivityLevel.MODERATE
    )
    goal = models.CharField(
        max_length=255, blank=True, help_text=_("Free-text wellness goal, e.g. 'lose 5kg'.")
    )

    def __str__(self) -> str:
        return f"Profile<{self.user.email}>"

    @property
    def age(self) -> int | None:
        if not self.date_of_birth:
            return None
        from datetime import date

        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )


class HealthHistoryEntry(TimeStampedModel):
    """Append-only medical/lifestyle history (conditions, allergies, notes).

    Kept separate from :class:`Profile` because it is a *timeline* of facts,
    not a single editable record — important context for both doctors and the
    AI coach's safety guardrail.
    """

    class Kind(models.TextChoices):
        CONDITION = "condition", _("Medical condition")
        ALLERGY = "allergy", _("Allergy")
        MEDICATION = "medication", _("Medication")
        INJURY = "injury", _("Injury")
        NOTE = "note", _("General note")

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="health_history"
    )
    kind = models.CharField(max_length=16, choices=Kind.choices)
    summary = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    recorded_on = models.DateField(null=True, blank=True)

    class Meta(TimeStampedModel.Meta):
        verbose_name_plural = "health history entries"

    def __str__(self) -> str:
        return f"{self.get_kind_display()}: {self.summary}"
