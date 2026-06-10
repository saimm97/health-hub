"""Signal handlers for the accounts app."""
from __future__ import annotations

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile, User


@receiver(post_save, sender=User)
def create_profile_for_new_user(sender, instance: User, created: bool, **kwargs) -> None:
    """Every user gets exactly one profile, created lazily on first save."""
    if created:
        Profile.objects.get_or_create(user=instance)
