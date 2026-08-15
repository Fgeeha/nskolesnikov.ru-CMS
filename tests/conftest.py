"""Shared pytest fixtures. No network access, no external services."""

from datetime import date

import pytest
from cms.utils.permissions import set_current_user
from django.utils import timezone

from apps.blog.models import Article, ArticleStatus, Category, Tag
from apps.core.models import SiteSettings
from apps.portfolio.models import (
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


@pytest.fixture(autouse=True)
def _reset_cms_current_user():
    """Drop the current user django CMS keeps in a thread local.

    `CurrentUserMiddleware` sets it on every request and never clears it, so a
    user from a previous test survives into the next one. With
    `CMS_PERMISSION=True` the post-save signal would then write a `PageUser`
    row pointing at an `auth_user` that the earlier transaction already rolled
    back, and PostgreSQL rejects it at teardown.
    """
    set_current_user(None)
    yield
    set_current_user(None)


@pytest.fixture
def site_settings(db) -> SiteSettings:
    return SiteSettings.objects.create(
        site_name="Тестовый сайт",
        tagline="Подзаголовок",
        default_seo_description="Описание по умолчанию",
    )


@pytest.fixture
def profile(db) -> DeveloperProfile:
    return DeveloperProfile.objects.create(
        full_name="Никита Колесников",
        nickname="fgeeha",
        headline="Python / Go Developer",
        summary="Краткое описание профиля.",
        biography="Расширенное описание профиля.",
        location="Россия",
        public_email="test@example.com",
        phone="+7 900 000-00-00",
    )


@pytest.fixture
def skill_category(db) -> SkillCategory:
    return SkillCategory.objects.create(name="Языки", slug="languages", order=10)


@pytest.fixture
def skill(skill_category: SkillCategory) -> Skill:
    return Skill.objects.create(
        name="Python", category=skill_category, level="основной", is_featured=True
    )


@pytest.fixture
def project_category(db) -> ProjectCategory:
    return ProjectCategory.objects.create(name="AI", slug="ai", order=10)


@pytest.fixture
def project(project_category: ProjectCategory, skill: Skill) -> Project:
    obj = Project.objects.create(
        title="Проект RAG",
        slug="rag-project",
        summary="Короткое описание проекта.",
        description="Полное описание проекта.",
        category=project_category,
        repository_url="https://example.com/repo",
        is_featured=True,
        is_published=True,
        started_on=date(2025, 1, 1),
    )
    obj.technologies.add(skill)
    return obj


@pytest.fixture
def draft_project(db) -> Project:
    return Project.objects.create(
        title="Черновик",
        slug="draft-project",
        summary="Не должен быть виден.",
        is_published=False,
    )


@pytest.fixture
def mini_project(db) -> MiniProject:
    return MiniProject.objects.create(
        title="Password Generator",
        slug="password-generator",
        summary="Генератор паролей.",
        url="https://example.com/tools/password",
    )


@pytest.fixture
def blog_category(db) -> Category:
    return Category.objects.create(name="Инженерия", slug="engineering", order=10)


@pytest.fixture
def tag(db) -> Tag:
    return Tag.objects.create(name="rag", slug="rag")


@pytest.fixture
def article(blog_category: Category, tag: Tag) -> Article:
    obj = Article.objects.create(
        title="Опубликованная статья",
        slug="published-article",
        excerpt="Превью статьи.",
        body="Текст статьи " * 50,
        category=blog_category,
        status=ArticleStatus.PUBLISHED,
        published_at=timezone.now(),
    )
    obj.tags.add(tag)
    return obj


@pytest.fixture
def draft_article(db) -> Article:
    return Article.objects.create(
        title="Черновик статьи",
        slug="draft-article",
        excerpt="Превью черновика.",
        body="Текст черновика.",
        status=ArticleStatus.DRAFT,
    )


@pytest.fixture
def social_link(db) -> SocialLink:
    return SocialLink.objects.create(
        name="GitHub", url="https://github.com/example", username="@example", order=10
    )


@pytest.fixture
def experience(skill: Skill) -> Experience:
    obj = Experience.objects.create(
        organization="ООО Пример",
        position="Backend-разработчик",
        started_on=date(2023, 1, 1),
        is_current=True,
    )
    obj.technologies.add(skill)
    return obj


@pytest.fixture
def education(db) -> Education:
    return Education.objects.create(
        institution="Университет",
        program="Информатика",
        degree="Бакалавр",
        started_on=date(2018, 9, 1),
        finished_on=date(2022, 6, 30),
    )


@pytest.fixture
def content(db, site_settings, profile, project, mini_project, article, social_link):
    """Full public dataset for view-level tests."""
    return None
