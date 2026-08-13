"""SEO helper tags: fallbacks and safe structured data."""

import json

import pytest
from django.template import Context, Template

from apps.core.templatetags.seo_tags import absolute_url

pytestmark = pytest.mark.django_db


def render(template: str, **context) -> str:
    return Template("{% load seo_tags %}" + template).render(Context(context))


def test_page_title_appends_site_name(site_settings):
    out = render("{% page_title %}", page_title="Проекты", site_settings=site_settings)
    assert out == "Проекты — Тестовый сайт"


def test_page_title_falls_back_to_site_name(site_settings):
    assert render("{% page_title %}", site_settings=site_settings) == "Тестовый сайт"


def test_page_description_falls_back_to_default(site_settings):
    out = render("{% page_description %}", site_settings=site_settings)
    assert out == "Описание по умолчанию"


def test_page_description_truncates_long_text_at_word_boundary(site_settings):
    long_excerpt = "слово " * 40  # 240 chars, well past the 160-char cap
    out = render(
        "{% page_description %}", meta_description=long_excerpt, site_settings=site_settings
    )
    assert len(out) <= 160
    assert out.endswith("…")
    assert not out.endswith(" …")


def test_absolute_url_leaves_external_links_untouched():
    assert absolute_url("https://example.com/x") == "https://example.com/x"


def test_absolute_url_prefixes_relative_paths():
    assert absolute_url("media/a.png") == "https://testserver/media/a.png"


def test_schema_person_is_valid_json(profile, site_settings, social_link):
    out = render(
        "{% schema_person %}",
        profile=profile,
        site_settings=site_settings,
        social_links=[social_link],
    )
    data = json.loads(out.replace("\\u003c", "<"))
    types = {node["@type"] for node in data["@graph"]}
    assert types == {"Person", "WebSite"}
    assert data["@graph"][0]["sameAs"] == [social_link.url]


def test_schema_person_is_empty_without_profile(site_settings):
    assert render("{% schema_person %}", site_settings=site_settings) == ""


def test_schema_escapes_closing_script_tag(profile, site_settings):
    profile.summary = "</script><img src=x>"
    out = render("{% schema_person %}", profile=profile, site_settings=site_settings)
    assert "</script>" not in out
    assert "\\u003c/script" in out


def test_schema_article_reports_blogposting(article):
    data = json.loads(render("{% schema_article article %}", article=article))
    assert data["@type"] == "BlogPosting"
    assert data["url"].endswith(article.get_absolute_url())


def test_schema_project_reports_repository(project):
    data = json.loads(render("{% schema_project project %}", project=project))
    assert data["@type"] == "SoftwareSourceCode"
    assert data["codeRepository"] == project.repository_url


def test_schema_breadcrumbs_lists_items_in_order():
    out = render("{% schema_breadcrumbs 'Статьи' '/blog/' 'Заголовок' '/blog/slug/' %}")
    data = json.loads(out)
    assert data["@type"] == "BreadcrumbList"
    assert [item["position"] for item in data["itemListElement"]] == [1, 2]
    assert data["itemListElement"][0] == {
        "@type": "ListItem",
        "position": 1,
        "name": "Статьи",
        "item": "https://testserver/blog/",
    }
    assert data["itemListElement"][1]["item"] == "https://testserver/blog/slug/"
