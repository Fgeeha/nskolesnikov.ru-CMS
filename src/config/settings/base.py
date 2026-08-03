"""Base Django settings shared by all environments."""

from pathlib import Path

import environ

# src/config/settings/base.py -> src/
SRC_DIR = Path(__file__).resolve().parents[2]
BASE_DIR = SRC_DIR.parent

env = environ.Env()
env.read_env(str(BASE_DIR / ".env"))


def env_list(name: str, default: list[str]) -> list[str]:
    """Read a comma-separated variable, treating an empty value as unset.

    `DJANGO_ALLOWED_HOSTS=` in a .env file would otherwise parse to `[""]`,
    which allows no host at all instead of falling back to the default.
    """
    values = [item.strip() for item in env.str(name, default="").split(",")]
    cleaned = [item for item in values if item]
    return cleaned or default


SECRET_KEY = env.str("DJANGO_SECRET_KEY", default="insecure-development-key")
DEBUG = env.bool("DJANGO_DEBUG", default=False)
ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# Absolute public URL used for canonical links, sitemaps and Open Graph tags.
SITE_URL = env.str("DJANGO_SITE_URL", default="http://localhost:8000").rstrip("/")
SITE_ID = 1

INSTALLED_APPS = [
    "djangocms_admin_style",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    # django CMS
    "cms",
    "menus",
    "treebeard",
    "sekizai",
    "djangocms_text",
    # Media library
    "filer",
    "easy_thumbnails",
    # Project applications
    "apps.core",
    "apps.portfolio",
    "apps.blog",
    "apps.contact",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "cms.middleware.utils.ApphookReloadMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [SRC_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "cms.context_processors.cms_settings",
                "apps.core.context_processors.site_context",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str("POSTGRES_DB", default="portfolio"),
        "USER": env.str("POSTGRES_USER", default="portfolio"),
        "PASSWORD": env.str("POSTGRES_PASSWORD", default=""),
        "HOST": env.str("POSTGRES_HOST", default="localhost"),
        "PORT": env.int("POSTGRES_PORT", default=5432),
        "CONN_MAX_AGE": env.int("POSTGRES_CONN_MAX_AGE", default=60),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Internationalization -------------------------------------------------
LANGUAGE_CODE = "ru"
TIME_ZONE = env.str("DJANGO_TIME_ZONE", default="Europe/Moscow")
USE_I18N = True
USE_TZ = True

LANGUAGES = [
    ("ru", "Русский"),
    ("en", "English"),
]

LOCALE_PATHS = [SRC_DIR / "locale"]

# The English tree is prepared but not published by default; adding it is a
# content task, not a code change.
CMS_LANGUAGES = {
    1: [
        {
            "code": "ru",
            "name": "Русский",
            "public": True,
            "redirect_on_fallback": True,
            "hide_untranslated": False,
        },
        {
            "code": "en",
            "name": "English",
            "public": True,
            "fallbacks": ["ru"],
            "redirect_on_fallback": False,
            "hide_untranslated": False,
        },
    ],
    "default": {
        "public": True,
        "fallbacks": ["ru"],
        "hide_untranslated": False,
        "redirect_on_fallback": True,
    },
}

# --- Static and media -----------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [SRC_DIR / "static"]

MEDIA_URL = "/media/"
MEDIA_ROOT = env.str("DJANGO_MEDIA_ROOT", default=str(SRC_DIR / "media"))

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# --- django CMS -----------------------------------------------------------
CMS_TEMPLATES = [
    ("cms/home.html", "Главная страница"),
    ("cms/page.html", "Обычная страница"),
    ("cms/fullwidth.html", "Страница без боковых отступов"),
]

# Required by django CMS 4+/5: acknowledges the versioned page-content model.
CMS_CONFIRM_VERSION4 = True

CMS_PERMISSION = True
CMS_PLACEHOLDER_CONF: dict[str, object] = {}

X_FRAME_OPTIONS = "SAMEORIGIN"

TEXT_INLINE_EDITING = True

THUMBNAIL_HIGH_RESOLUTION = True
THUMBNAIL_PROCESSORS = (
    "easy_thumbnails.processors.colorspace",
    "easy_thumbnails.processors.autocrop",
    "filer.thumbnail_processors.scale_and_crop_with_subject_location",
    "easy_thumbnails.processors.filters",
)
FILER_IMAGE_USE_ICON = True

# --- Email ----------------------------------------------------------------
EMAIL_BACKEND = env.str("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = env.str("EMAIL_HOST", default="")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env.bool("EMAIL_USE_TLS", default=True)
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="noreply@example.com")
# Address receiving contact form notifications; empty disables notifications.
CONTACT_EMAIL = env.str("CONTACT_EMAIL", default="")

# Minimum seconds between two submissions from the same client.
CONTACT_RATE_LIMIT_SECONDS = env.int("CONTACT_RATE_LIMIT_SECONDS", default=60)

# --- Logging --------------------------------------------------------------
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": env.str("DJANGO_LOG_LEVEL", default="INFO"),
    },
    "loggers": {
        "django.db.backends": {"level": "WARNING", "handlers": ["console"], "propagate": False},
    },
}
