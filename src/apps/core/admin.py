from django.contrib import admin
from django.http import HttpRequest

from apps.core.models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "tagline")
    fieldsets = (
        (None, {"fields": ("site_name", "tagline", "footer_text")}),
        (
            "SEO по умолчанию",
            {"fields": ("default_seo_title", "default_seo_description", "default_og_image")},
        ),
        (
            "Индексация",
            {"fields": ("robots_extra", "yandex_verification", "google_verification")},
        ),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        # Singleton: allow creating the first row only.
        return not SiteSettings.objects.exists()
