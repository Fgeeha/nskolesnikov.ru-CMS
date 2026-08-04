"""Production settings: strict secrets, HTTPS hardening, reverse proxy aware."""

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403
from .base import env, env_list


def required_list(name: str) -> list[str]:
    """Comma-separated variable that must be present and non-empty."""
    values = env_list(name, default=[])
    if not values:
        raise ImproperlyConfigured(f"Set the {name} environment variable")
    return values


DEBUG = False

# No insecure fallbacks in production: the process must fail loudly instead of
# silently running with a known key or an open host list.
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ImproperlyConfigured("Set the DJANGO_SECRET_KEY environment variable")
ALLOWED_HOSTS = required_list("DJANGO_ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = required_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# Gunicorn sits behind Nginx, which terminates TLS and forwards the scheme.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"

# security.W019 expects X_FRAME_OPTIONS="DENY", but django CMS renders its
# structure board and plugin editors in same-origin iframes, so "SAMEORIGIN"
# (set in base.py) is required for the CMS to work at all.
SILENCED_SYSTEM_CHECKS = ["security.W019"]

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Lax"
LANGUAGE_COOKIE_SECURE = True

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"},
}

DATA_UPLOAD_MAX_MEMORY_SIZE = env.int("DJANGO_DATA_UPLOAD_MAX_MEMORY_SIZE", default=5 * 1024 * 1024)
FILE_UPLOAD_MAX_MEMORY_SIZE = DATA_UPLOAD_MAX_MEMORY_SIZE
