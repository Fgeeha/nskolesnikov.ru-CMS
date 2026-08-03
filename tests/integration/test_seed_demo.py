"""seed_demo must be safe to run repeatedly."""

import pytest
from django.core.management import call_command

from apps.blog.models import Article
from apps.core.models import SiteSettings
from apps.portfolio.models import (
    DeveloperProfile,
    MiniProject,
    Project,
    Skill,
    SocialLink,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def seeded(db):
    call_command("seed_demo", verbosity=0)


def test_creates_expected_content(seeded):
    assert DeveloperProfile.objects.count() == 1
    assert SiteSettings.objects.count() == 1
    assert Skill.objects.exists()
    assert Project.objects.published().exists()
    assert MiniProject.objects.active().exists()
    assert SocialLink.objects.visible().exists()
    assert Article.objects.published().exists()


def test_second_run_creates_no_duplicates(seeded):
    counts = {
        model: model.objects.count()
        for model in (
            DeveloperProfile,
            SiteSettings,
            Skill,
            Project,
            MiniProject,
            SocialLink,
            Article,
        )
    }
    call_command("seed_demo", verbosity=0)
    for model, count in counts.items():
        assert model.objects.count() == count, model.__name__


def test_second_run_keeps_publication_date(seeded):
    original = Article.objects.published().first().published_at
    call_command("seed_demo", verbosity=0)
    assert Article.objects.published().first().published_at == original


def test_dry_run_writes_nothing(db):
    call_command("seed_demo", "--dry-run", verbosity=0)
    assert Project.objects.count() == 0
    assert DeveloperProfile.objects.count() == 0


def test_skip_pages_leaves_page_tree_empty(db):
    from cms.models import Page

    call_command("seed_demo", "--skip-pages", verbosity=0)
    assert Page.objects.count() == 0
    assert Project.objects.exists()
