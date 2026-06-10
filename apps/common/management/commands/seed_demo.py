"""
Seed the database with demo data so the app is usable immediately.

    python manage.py seed_demo

Idempotent: safe to run repeatedly (uses get_or_create).
"""
from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.billing.models import Plan
from apps.consultations.models import AvailabilitySlot, DoctorProfile
from apps.fitness.models import Exercise
from apps.nutrition.models import Food

User = get_user_model()

EXERCISES = [
    ("Barbell Bench Press", "chest", "barbell"),
    ("Pull-up", "back", "bodyweight"),
    ("Back Squat", "legs", "barbell"),
    ("Overhead Press", "shoulders", "barbell"),
    ("Plank", "core", "bodyweight"),
    ("Running", "cardio", "none"),
]

FOODS = [
    # name, kcal/100g, protein, carbs, fat
    ("Chicken breast", 165, 31, 0, 3.6),
    ("White rice (cooked)", 130, 2.7, 28, 0.3),
    ("Banana", 89, 1.1, 23, 0.3),
    ("Greek yogurt", 59, 10, 3.6, 0.4),
    ("Almonds", 579, 21, 22, 50),
]


class Command(BaseCommand):
    help = "Populate the database with demo data."

    def handle(self, *args, **options) -> None:
        for name, muscle, equipment in EXERCISES:
            Exercise.objects.get_or_create(
                name=name, defaults={"muscle_group": muscle, "equipment": equipment}
            )
        self.stdout.write(self.style.SUCCESS(f"Exercises: {Exercise.objects.count()}"))

        for name, kcal, p, c, f in FOODS:
            Food.objects.get_or_create(
                name=name,
                defaults={
                    "calories_per_100g": kcal,
                    "protein_g": p,
                    "carbs_g": c,
                    "fat_g": f,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Foods: {Food.objects.count()}"))

        Plan.objects.get_or_create(name="Free", defaults={"price_cents": 0})
        Plan.objects.get_or_create(
            name="Premium", defaults={"price_cents": 999, "interval": "month"}
        )
        self.stdout.write(self.style.SUCCESS(f"Plans: {Plan.objects.count()}"))

        # A seeded doctor (real telemedicine infra, no licensed doctor needed).
        doctor_user, _ = User.objects.get_or_create(
            email="dr.demo@healthhub.local",
            defaults={"full_name": "Dr. Demo", "role": User.Role.DOCTOR},
        )
        doctor, _ = DoctorProfile.objects.get_or_create(
            user=doctor_user,
            defaults={"specialty": "Sports Medicine", "years_experience": 8},
        )
        # A few open slots over the next few days.
        base = timezone.now().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
        for day in range(3):
            start = base + timedelta(days=day)
            AvailabilitySlot.objects.get_or_create(
                doctor=doctor,
                starts_at=start,
                defaults={"ends_at": start + timedelta(minutes=30)},
            )
        self.stdout.write(self.style.SUCCESS(f"Slots: {AvailabilitySlot.objects.count()}"))
        self.stdout.write(self.style.SUCCESS("Demo data seeded."))
