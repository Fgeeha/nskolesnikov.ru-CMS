"""Health check, robots.txt, sitemap and admin registration."""

import json
from unittest import mock

import pytest
from django.contrib import admin
from django.db import DatabaseError
from django.test import RequestFactory
from django.urls import reverse

from apps.blog.models import Article, Category, Tag
from apps.contact.models import ContactMessage
from apps.core.models import SiteSettings
from apps.core.views import health
from apps.portfolio.models import (
    Certificate,
    DeveloperProfile,
    Education,
    Experience,
    MiniProject,
    Project,
    ProjectCategory,
    Skill,
    SkillCategory,
    SocialLink,
)

pytestmark = pytest.mark.django_db


class TestHealth:
    def test_reports_ok(self, client):
        response = client.get(reverse("health"))
        assert response.status_code == 200
        assert json.loads(response.content) == {"status": "ok", "database": "ok"}

    def test_reports_503_when_database_is_down(self):
        # Called without middleware: the patch must only affect the view's own
        # cursor call, not session or CMS queries around it.
        request = RequestFactory().get("/health/")
        with mock.patch("apps.core.views.connection.cursor", side_effect=DatabaseError("down")):
            response = health(request)
        assert response.status_code == 503
        assert json.loads(response.content)["status"] == "error"

    def test_response_is_not_cached(self, client):
        assert "no-cache" in client.get(reverse("health")).headers.get("Cache-Control", "")


class TestRobots:
    def test_serves_plain_text_with_absolute_sitemap(self, client, site_settings):
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert response["Content-Type"].startswith("text/plain")
        body = response.content.decode()
        assert "Disallow: /admin/" in body
        assert "Sitemap: http://testserver/sitemap.xml" in body

    def test_extra_lines_are_appended(self, client, site_settings):
        site_settings.robots_extra = "Disallow: /private/"
        site_settings.save(update_fields=["robots_extra"])
        assert "Disallow: /private/" in client.get("/robots.txt").content.decode()

    def test_works_without_site_settings_row(self, client):
        assert client.get("/robots.txt").status_code == 200


class TestSitemap:
    def test_lists_published_content_only(self, client, content, project, article):
        body = client.get("/sitemap.xml").content.decode()
        assert project.get_absolute_url() in body
        assert article.get_absolute_url() in body

    def test_excludes_drafts(self, client, content, draft_project, draft_article):
        body = client.get("/sitemap.xml").content.decode()
        assert draft_project.get_absolute_url() not in body
        assert draft_article.get_absolute_url() not in body

    def test_includes_static_sections(self, client, content):
        body = client.get("/sitemap.xml").content.decode()
        for name in ("portfolio:about", "portfolio:resume", "blog:article-list"):
            assert reverse(name) in body


@pytest.mark.parametrize(
    "model",
    [
        SiteSettings,
        DeveloperProfile,
        SkillCategory,
        Skill,
        ProjectCategory,
        Project,
        MiniProject,
        Experience,
        Education,
        Certificate,
        SocialLink,
        Category,
        Tag,
        Article,
        ContactMessage,
    ],
)
def test_model_is_registered_in_admin(model):
    assert model in admin.site._registry


class TestAdminAccess:
    def test_contact_messages_cannot_be_added_manually(self, admin_client):
        response = admin_client.get("/admin/contact/contactmessage/add/")
        assert response.status_code in (403, 302)

    def test_project_changelist_is_reachable(self, admin_client, project):
        response = admin_client.get("/admin/portfolio/project/")
        assert response.status_code == 200
        assert project.title in response.content.decode()

    def test_anonymous_admin_is_redirected(self, client):
        response = client.get("/admin/portfolio/project/")
        assert response.status_code == 302
        assert "/admin/login/" in response.url
