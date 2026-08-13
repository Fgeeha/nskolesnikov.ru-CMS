"""Model behaviour: querysets, constraints, ordering and derived values."""

from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.blog.models import Article, ArticleStatus
from apps.core.models import SiteSettings
from apps.portfolio.models import (
    DeveloperProfile,
    Education,
    Experience,
    Project,
    Skill,
    SkillCategory,
    SocialLink,
)

pytestmark = pytest.mark.django_db


class TestProjectQuerySet:
    def test_published_excludes_unpublished(self, project, draft_project):
        slugs = set(Project.objects.published().values_list("slug", flat=True))
        assert project.slug in slugs
        assert draft_project.slug not in slugs

    def test_featured_is_published_only(self, project, draft_project):
        draft_project.is_featured = True
        draft_project.save(update_fields=["is_featured"])
        assert list(Project.objects.featured()) == [project]

    def test_absolute_url_uses_slug(self, project):
        assert project.get_absolute_url() == f"/projects/{project.slug}/"

    def test_ordering_respects_order_field(self, project_category):
        second = Project.objects.create(
            title="Второй", slug="second", summary="s", order=5, category=project_category
        )
        first = Project.objects.create(
            title="Первый", slug="first", summary="s", order=1, category=project_category
        )
        assert list(Project.objects.all()) == [first, second]

    def test_finish_date_before_start_is_rejected(self):
        with pytest.raises(IntegrityError):
            Project.objects.create(
                title="Некорректные даты",
                slug="bad-dates",
                summary="s",
                started_on=date(2025, 5, 1),
                finished_on=date(2025, 1, 1),
            )


class TestSkill:
    def test_duplicate_name_in_category_is_rejected(self, skill, skill_category):
        with pytest.raises(IntegrityError):
            Skill.objects.create(name=skill.name, category=skill_category)

    def test_same_name_in_another_category_is_allowed(self, skill):
        other = SkillCategory.objects.create(name="Инструменты", slug="tools")
        assert Skill.objects.create(name=skill.name, category=other).pk

    def test_featured_queryset(self, skill, skill_category):
        Skill.objects.create(name="Rust", category=skill_category, is_featured=False)
        assert list(Skill.objects.featured()) == [skill]


class TestExperienceConstraints:
    def test_current_position_cannot_have_end_date(self):
        with pytest.raises(IntegrityError):
            Experience.objects.create(
                organization="ООО",
                position="Инженер",
                started_on=date(2023, 1, 1),
                finished_on=date(2024, 1, 1),
                is_current=True,
            )

    def test_end_before_start_is_rejected(self):
        with pytest.raises(IntegrityError):
            Education.objects.create(
                institution="Университет",
                program="Информатика",
                started_on=date(2022, 1, 1),
                finished_on=date(2020, 1, 1),
            )


class TestArticleQuerySet:
    def test_published_excludes_drafts(self, article, draft_article):
        assert list(Article.objects.published()) == [article]

    def test_future_publication_is_not_public(self, blog_category):
        future = Article.objects.create(
            title="Из будущего",
            slug="future",
            excerpt="e",
            body="b",
            status=ArticleStatus.PUBLISHED,
            published_at=timezone.now() + timedelta(days=1),
        )
        assert future not in Article.objects.published()
        assert future.is_published is False

    def test_reading_time_is_estimated_when_unset(self, article):
        assert article.reading_time == 0
        assert article.estimated_reading_time >= 1

    def test_stored_reading_time_wins(self, article):
        article.reading_time = 9
        assert article.estimated_reading_time == 9

    def test_reading_time_ignores_html_markup(self):
        # 269 real words rounds down to 1 minute; if block tags on their own
        # lines were counted as extra words (no strip_tags), it rounds up to 2.
        marked_up = Article.objects.create(
            title="С разметкой",
            slug="marked-up",
            excerpt="e",
            body="<p>\n" + "слово " * 269 + "\n</p>",
        )
        assert marked_up.estimated_reading_time == 1

    def test_absolute_url_uses_slug(self, article):
        assert article.get_absolute_url() == f"/blog/{article.slug}/"


class TestSingletons:
    def test_second_profile_is_rejected_by_clean(self, profile):
        with pytest.raises(ValidationError):
            DeveloperProfile(full_name="Другой", headline="h", summary="s").clean()

    def test_second_site_settings_is_rejected_by_clean(self, site_settings):
        with pytest.raises(ValidationError):
            SiteSettings().clean()

    def test_get_solo_does_not_write(self, db):
        assert SiteSettings.objects.count() == 0
        obj = SiteSettings.get_solo()
        assert obj.pk is None
        assert SiteSettings.objects.count() == 0

    def test_display_name_includes_nickname(self, profile):
        assert profile.display_name == "Никита Колесников (fgeeha)"


class TestSocialLink:
    def test_visible_queryset(self, social_link):
        SocialLink.objects.create(name="Hidden", url="https://example.com", is_visible=False)
        assert list(SocialLink.objects.visible()) == [social_link]
