"""Test settings — fast, isolated, deterministic."""
from __future__ import annotations

from .base import *  # noqa: F401,F403

# In-memory SQLite for speed.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Run Celery tasks synchronously so tests don't need a broker.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Fast, weak password hashing for the test suite only.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
