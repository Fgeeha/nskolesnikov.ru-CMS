"""Settings modules must differ where it matters for security."""

import importlib
import os
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured


def load(module: str, **env):
    """Import a settings module with a controlled environment."""
    with mock.patch.dict(os.environ, env, clear=False):
        return importlib.reload(importlib.import_module(module))


PROD_ENV = {
    "DJANGO_SECRET_KEY": "prod-secret",
    "DJANGO_ALLOWED_HOSTS": "example.com,www.example.com",
    "DJANGO_CSRF_TRUSTED_ORIGINS": "https://example.com",
}


class TestEnvList:
    def test_empty_value_falls_back_to_the_default(self):
        development = load("config.settings.development", DJANGO_ALLOWED_HOSTS="")
        assert development.ALLOWED_HOSTS == ["*"]

    def test_values_are_split_and_stripped(self):
        development = load(
            "config.settings.development", DJANGO_ALLOWED_HOSTS=" a.test , b.test ,, "
        )
        assert development.ALLOWED_HOSTS == ["a.test", "b.test"]


class TestProduction:
    def test_debug_is_off_and_secrets_are_required(self):
        production = load("config.settings.production", **PROD_ENV)
        assert production.DEBUG is False
        assert production.SECRET_KEY == "prod-secret"
        assert production.ALLOWED_HOSTS == ["example.com", "www.example.com"]

    def test_empty_allowed_hosts_fails_loudly(self):
        # Пустая строка не должна превращаться в [""] — это запретило бы всё.
        with (
            mock.patch.dict(os.environ, PROD_ENV | {"DJANGO_ALLOWED_HOSTS": ""}, clear=True),
            pytest.raises(ImproperlyConfigured),
        ):
            importlib.reload(importlib.import_module("config.settings.production"))

    def test_missing_secret_key_fails_loudly(self):
        env = {k: v for k, v in PROD_ENV.items() if k != "DJANGO_SECRET_KEY"}
        with (
            mock.patch.dict(os.environ, env, clear=True),
            pytest.raises(ImproperlyConfigured),
        ):
            importlib.reload(importlib.import_module("config.settings.production"))

    def test_transport_security_is_enabled(self):
        production = load("config.settings.production", **PROD_ENV)
        assert production.SESSION_COOKIE_SECURE is True
        assert production.CSRF_COOKIE_SECURE is True
        assert production.SECURE_HSTS_SECONDS >= 31536000
        assert production.SECURE_CONTENT_TYPE_NOSNIFF is True

    def test_reverse_proxy_header_is_configured(self):
        production = load("config.settings.production", **PROD_ENV)
        assert production.SECURE_PROXY_SSL_HEADER == ("HTTP_X_FORWARDED_PROTO", "https")

    def test_static_files_are_hashed(self):
        production = load("config.settings.production", **PROD_ENV)
        assert "Manifest" in production.STORAGES["staticfiles"]["BACKEND"]


class TestDevelopment:
    def test_hsts_is_not_enabled(self):
        development = load("config.settings.development")
        assert development.SECURE_HSTS_SECONDS == 0
        assert development.SECURE_SSL_REDIRECT is False
        assert development.SESSION_COOKIE_SECURE is False

    def test_any_host_is_allowed_by_default(self):
        # Сайт должен открываться по LAN-адресу машины без правки конфигурации.
        with mock.patch.dict(os.environ, {}, clear=True):
            development = importlib.reload(importlib.import_module("config.settings.development"))
        assert development.ALLOWED_HOSTS == ["*"]

    def test_explicit_hosts_win_over_the_default(self):
        development = load("config.settings.development", DJANGO_ALLOWED_HOSTS="example.test")
        assert development.ALLOWED_HOSTS == ["example.test"]


class TestBase:
    def test_russian_is_the_primary_language(self, settings):
        assert settings.LANGUAGE_CODE == "ru"
        assert [code for code, _ in settings.LANGUAGES] == ["ru", "en"]

    def test_english_tree_is_prepared(self, settings):
        codes = [entry["code"] for entry in settings.CMS_LANGUAGES[1]]
        assert codes == ["ru", "en"]

    def test_cms_templates_are_declared(self, settings):
        templates = dict(settings.CMS_TEMPLATES)
        assert "cms/home.html" in templates
        assert "cms/page.html" in templates

    def test_postgresql_is_the_default_engine(self):
        base = importlib.import_module("config.settings.base")
        assert base.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"

    def test_tests_run_on_postgresql(self, settings):
        # Тот же движок, что и в production: иначе ограничения базы и поведение
        # транзакций проверялись бы не по-настоящему.
        assert settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql"
