"""DRF serializers for the accounts app."""
from __future__ import annotations

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.accounts.models import HealthHistoryEntry, Profile

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    age = serializers.IntegerField(read_only=True)

    class Meta:
        model = Profile
        fields = [
            "date_of_birth",
            "sex",
            "height_cm",
            "activity_level",
            "goal",
            "age",
        ]


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role", "profile"]
        read_only_fields = ["id", "role"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ["id", "email", "full_name", "role", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data: dict):
        # Defer to the service layer so registration logic lives in one place.
        from apps.accounts.services import register_user

        return register_user(**validated_data)


class HealthHistoryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthHistoryEntry
        fields = ["id", "kind", "summary", "details", "recorded_on", "created"]
        read_only_fields = ["id", "created"]
