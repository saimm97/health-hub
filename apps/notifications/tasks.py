"""Asynchronous notification tasks (run by Celery workers)."""
from __future__ import annotations

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_email(*, to: str, subject: str, body: str) -> None:
    """Send a transactional email out-of-band so web requests stay fast."""
    send_mail(
        subject=subject,
        message=body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[to],
        fail_silently=False,
    )
