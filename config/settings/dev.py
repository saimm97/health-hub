"""Development settings — convenient, verbose, not safe for production."""
from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Print emails to the console instead of sending them.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Allow any localhost origin during development.
CORS_ALLOW_ALL_ORIGINS = True

INSTALLED_APPS += ["django_extensions"] if env.bool("USE_DJANGO_EXTENSIONS", default=False) else []  # noqa: F405
