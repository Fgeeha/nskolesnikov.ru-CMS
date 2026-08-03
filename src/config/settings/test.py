"""Test settings: isolated, fast, no external services."""

from .base import *  # noqa: F403
from .base import env

DEBUG = False
SECRET_KEY = "test-secret-key-not-used-anywhere-else"  # noqa: S105
ALLOWED_HOSTS = ["*"]

# Тесты идут на том же движке, что и production, поэтому ограничения базы,
# типы полей и поведение транзакций проверяются по-настоящему. Контейнер
# поднимается через infra/compose/compose.test.yml (`make test-db-up`).
DATABASES = {
    "default": env.db_url(
        "TEST_DATABASE_URL",
        default="postgres://portfolio:portfolio@127.0.0.1:55432/portfolio",
    )
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
CONTACT_EMAIL = "owner@example.com"
CONTACT_RATE_LIMIT_SECONDS = 0

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

SITE_URL = "https://testserver"

# Silence application logging; noisy tracebacks belong to the assertions.
LOGGING["root"]["level"] = "CRITICAL"  # type: ignore[index]  # noqa: F405
