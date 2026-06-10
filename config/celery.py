"""Celery application bootstrap."""
from __future__ import annotations

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("healthhub")

# Read CELERY_* settings from Django settings.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py modules in every installed app.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self) -> None:  # pragma: no cover
    print(f"Request: {self.request!r}")
