"""CMS page tree: the home page is composable and served from placeholders."""

import pytest
from cms.models import Page, Placeholder
from django.contrib.auth.models import User

from apps.core.management.commands._demo_pages import seed_home_page

pytestmark = pytest.mark.django_db


@pytest.fixture
def home_page(db) -> Page:
    seed_home_page()
    return Page.objects.get(is_home=True)


def test_seed_creates_home_page_with_plugins(home_page):
    content = home_page.pagecontent_set(manager="admin_manager").get(language="ru")
    placeholders = Placeholder.objects.get_for_obj(content)
    slots = {ph.slot for ph in placeholders}
    assert {"hero", "sections", "closing"} <= slots

    total = sum(ph.cmsplugin_set.count() for ph in placeholders)
    assert total > 0


def test_seed_is_idempotent(home_page):
    before = Page.objects.count()
    report = seed_home_page()
    assert Page.objects.count() == before
    assert "уже существует" in report


def test_home_page_is_served_at_root(client, home_page, content):
    response = client.get("/")
    assert response.status_code == 200


def test_home_page_renders_plugin_content(client, home_page, content, project, profile):
    body = client.get("/").content.decode()
    assert profile.full_name in body
    assert project.title in body


def test_home_page_template_is_configurable(home_page):
    content = home_page.pagecontent_set(manager="admin_manager").get(language="ru")
    assert content.template == "cms/home.html"


def test_toolbar_is_available_to_staff(client, home_page, content):
    user = User.objects.create_superuser("editor", "editor@example.com", "pass1234")
    client.force_login(user)
    response = client.get("/?edit")
    assert response.status_code == 200
    assert "cms-toolbar" in response.content.decode()


def test_anonymous_visitor_gets_no_toolbar(client, home_page, content):
    assert "cms-toolbar" not in client.get("/").content.decode()
