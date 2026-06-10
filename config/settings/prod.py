"""Production settings — secure defaults; everything sensitive comes from env."""
from __future__ import annotations

from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

# SECRET_KEY, ALLOWED_HOSTS and DATABASE_URL must be provided via the
# environment in production — there are no insecure fallbacks here.
SECRET_KEY = env("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

# Security hardening.
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=60 * 60 * 24 * 30)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Real email backend (SMTP) in production.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True
