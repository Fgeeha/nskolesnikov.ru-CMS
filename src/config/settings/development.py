"""Development settings: verbose errors, no transport hardening."""

from .base import *  # noqa: F403
from .base import env, env_list

DEBUG = env.bool("DJANGO_DEBUG", default=True)

# По умолчанию хосты не проверяются: сайт открывается и по localhost, и по
# LAN-адресу машины (телефон, вторая машина, VM) без правки конфигурации.
# Это безопасно только потому, что production-настройки живут в отдельном
# модуле и требуют явного DJANGO_ALLOWED_HOSTS без запасного значения.
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default=["*"])

CSRF_TRUSTED_ORIGINS = env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    default=["http://localhost:8000", "http://127.0.0.1:8000"],
)

INTERNAL_IPS = ["127.0.0.1"]

# HSTS и secure cookies намеренно выключены: локальная разработка идёт по
# обычному HTTP, а включённый HSTS заставил бы браузер запомнить принудительный
# HTTPS для localhost.
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

EMAIL_BACKEND = env.str("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
