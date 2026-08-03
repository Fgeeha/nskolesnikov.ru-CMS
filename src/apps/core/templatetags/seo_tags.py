"""Template tags that resolve SEO values with sensible fallbacks."""

import json
from typing import Any

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


def _settings_obj(context: template.Context) -> Any:
    return context.get("site_settings")


@register.simple_tag(takes_context=True)
def page_title(context: template.Context) -> str:
    """Page title: view value, then CMS page title, then site defaults."""
    site = _settings_obj(context)
    site_name = getattr(site, "site_name", "") or "Портфолио"

    explicit = context.get("page_title")
    if not explicit:
        cms_page = context.get("current_page")
        explicit = getattr(cms_page, "get_page_title", lambda: "")() if cms_page else ""

    if explicit and explicit != site_name:
        return f"{explicit} — {site_name}"
    return getattr(site, "default_seo_title", "") or site_name


@register.simple_tag(takes_context=True)
def page_description(context: template.Context) -> str:
    """Meta description: view value, then CMS page description, then default."""
    explicit = context.get("meta_description")
    if not explicit:
        cms_page = context.get("current_page")
        explicit = getattr(cms_page, "get_meta_description", lambda: "")() if cms_page else ""
    if explicit:
        return str(explicit)
    site = _settings_obj(context)
    return getattr(site, "default_seo_description", "") or getattr(site, "tagline", "") or ""


@register.simple_tag(takes_context=True)
def canonical_url(context: template.Context) -> str:
    """Absolute canonical URL without query string."""
    request = context.get("request")
    if request is None:
        return settings.SITE_URL
    return f"{settings.SITE_URL}{request.path}"


@register.simple_tag
def absolute_url(path: str) -> str:
    """Turn a relative path or file URL into an absolute one."""
    if not path:
        return ""
    if path.startswith(("http://", "https://")):
        return path
    return f"{settings.SITE_URL}{path if path.startswith('/') else '/' + path}"


def _json_ld(data: dict[str, Any]) -> str:
    """Serialise structured data safely for inline <script> embedding."""
    payload = json.dumps(data, ensure_ascii=False)
    # Prevent an early </script> from breaking out of the tag.
    return mark_safe(payload.replace("<", "\\u003c"))  # noqa: S308 - escaped above


@register.simple_tag(takes_context=True)
def schema_person(context: template.Context) -> str:
    """Schema.org Person + WebSite graph for the site owner."""
    profile = context.get("profile")
    if profile is None:
        return ""
    site = _settings_obj(context)
    person: dict[str, Any] = {
        "@type": "Person",
        "name": profile.full_name,
        "jobTitle": profile.headline,
        "description": profile.summary,
        "url": settings.SITE_URL,
    }
    if profile.nickname:
        person["alternateName"] = profile.nickname
    if profile.location:
        person["address"] = {"@type": "PostalAddress", "addressLocality": profile.location}
    same_as = [link.url for link in context.get("social_links") or []]
    if same_as:
        person["sameAs"] = same_as

    website = {
        "@type": "WebSite",
        "name": getattr(site, "site_name", "") or profile.full_name,
        "url": settings.SITE_URL,
        "inLanguage": "ru-RU",
    }
    return _json_ld({"@context": "https://schema.org", "@graph": [person, website]})


@register.simple_tag
def schema_article(article: Any) -> str:
    """Schema.org BlogPosting for a single article."""
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": article.title,
        "description": article.excerpt,
        "url": f"{settings.SITE_URL}{article.get_absolute_url()}",
        "datePublished": article.published_at.isoformat() if article.published_at else None,
        "dateModified": article.updated_at.isoformat(),
        "inLanguage": "ru-RU",
    }
    if article.cover:
        data["image"] = absolute_url(article.cover.url)
    return _json_ld({k: v for k, v in data.items() if v is not None})


@register.simple_tag
def schema_project(project: Any) -> str:
    """Schema.org SoftwareSourceCode for an open-source project."""
    data: dict[str, Any] = {
        "@context": "https://schema.org",
        "@type": "SoftwareSourceCode",
        "name": project.title,
        "description": project.summary,
        "url": f"{settings.SITE_URL}{project.get_absolute_url()}",
        "codeRepository": project.repository_url or None,
        "programmingLanguage": [skill.name for skill in project.technologies.all()] or None,
    }
    return _json_ld({k: v for k, v in data.items() if v is not None})
