"""Infrastructure views: health check, robots.txt and error handlers."""

import logging

from django.db import DatabaseError, connection
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache

from apps.core.models import SiteSettings

logger = logging.getLogger(__name__)


@never_cache
def health(request: HttpRequest) -> JsonResponse:
    """Report application and database availability."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        logger.exception("Health check failed: database is unreachable")
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "database": "ok"})


@never_cache
def robots_txt(request: HttpRequest) -> HttpResponse:
    """Serve robots.txt with an absolute sitemap URL."""
    settings_obj = SiteSettings.get_solo()
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /filer/",
        "Disallow: /i18n/",
        "Allow: /",
        "",
        f"Sitemap: {sitemap_url}",
    ]
    if settings_obj.robots_extra:
        lines.extend(["", settings_obj.robots_extra.strip()])
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain; charset=utf-8")


def privacy_policy(request: HttpRequest) -> HttpResponse:
    """Personal data processing policy (152-ФЗ)."""
    context = {
        "page_title": "Политика обработки персональных данных",
        "meta_description": (
            "Политика обработки персональных данных оператора персональных данных."
        ),
    }
    return render(request, "core/privacy.html", context)


def cookie_policy(request: HttpRequest) -> HttpResponse:
    """Cookie usage policy."""
    context = {
        "page_title": "Политика использования cookie",
        "meta_description": "Как сайт использует файлы cookie и как их отключить.",
    }
    return render(request, "core/cookies.html", context)


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "404.html", status=404)


def server_error(request: HttpRequest) -> HttpResponse:
    return render(request, "500.html", status=500)
