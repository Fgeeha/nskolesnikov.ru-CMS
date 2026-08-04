"""Site-wide template context."""

from typing import Any

from django.http import HttpRequest

from apps.core.models import SiteSettings
from apps.portfolio.models import DeveloperProfile, SocialLink

CACHE_ATTR = "_site_context_cache"


def site_context(request: HttpRequest) -> dict[str, Any]:
    """Expose site settings, profile and social links to every template.

    Each entry is a single indexed lookup and the result is cached on the
    request, so navigation and footer rendering stay at a constant query cost.
    """
    cached: dict[str, Any] | None = getattr(request, CACHE_ATTR, None)
    if cached is not None:
        return cached

    context: dict[str, Any] = {
        "site_settings": SiteSettings.get_solo(),
        "profile": DeveloperProfile.objects.first(),
        "social_links": list(SocialLink.objects.visible()),
    }
    setattr(request, CACHE_ATTR, context)
    return context
