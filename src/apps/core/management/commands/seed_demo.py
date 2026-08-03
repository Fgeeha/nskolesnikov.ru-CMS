"""Populate the database with demonstration content.

Idempotent: every object is written through ``update_or_create`` keyed on a
stable natural key, so repeated runs update rather than duplicate.
"""

from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction
from django.utils import timezone

from apps.blog.models import Article, ArticleStatus, Category
from apps.core.management.commands import _demo_data as data
from apps.core.management.commands._demo_pages import seed_home_page
from apps.core.models import SiteSettings
from apps.portfolio.models import (
    DeveloperProfile,
    MiniProject,
    Project,
    ProjectCategory,
    Skill,
    SkillCategory,
    SocialLink,
)


class Command(BaseCommand):
    help = "Создаёт или обновляет демонстрационные данные портфолио."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Показать план без записи в базу.",
        )
        parser.add_argument(
            "--skip-pages",
            action="store_true",
            help="Не создавать главную страницу django CMS.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        dry_run: bool = options["dry_run"]

        if dry_run:
            self.stdout.write("Режим --dry-run: изменения не сохраняются.")

        with transaction.atomic():
            counts = self._seed()
            page_report = "" if options["skip_pages"] else seed_home_page()
            if dry_run:
                transaction.set_rollback(True)

        for label, value in counts.items():
            self.stdout.write(f"{label}: {value}")
        if page_report:
            self.stdout.write(page_report)
        self.stdout.write(self.style.SUCCESS("Демонстрационные данные готовы."))

    def _seed(self) -> dict[str, int]:
        # Both are singletons: update the existing row instead of adding one.
        site_settings = SiteSettings.objects.first() or SiteSettings()
        for field, value in data.SITE_SETTINGS.items():
            setattr(site_settings, field, value)
        site_settings.save()

        profile = DeveloperProfile.objects.first() or DeveloperProfile()
        for profile_field, profile_value in data.PROFILE.items():
            setattr(profile, profile_field, profile_value)
        profile.save()

        skill_categories: dict[str, SkillCategory] = {}
        for name, slug, order in data.SKILL_CATEGORIES:
            skill_categories[slug], _ = SkillCategory.objects.update_or_create(
                slug=slug, defaults={"name": name, "order": order}
            )

        skills: dict[str, Skill] = {}
        for name, category_slug, level, featured, order in data.SKILLS:
            skills[name], _ = Skill.objects.update_or_create(
                category=skill_categories[category_slug],
                name=name,
                defaults={"level": level, "is_featured": featured, "order": order},
            )

        project_categories: dict[str, ProjectCategory] = {}
        for name, slug, description, order in data.PROJECT_CATEGORIES:
            project_categories[slug], _ = ProjectCategory.objects.update_or_create(
                slug=slug,
                defaults={"name": name, "description": description, "order": order},
            )

        for row in data.PROJECTS:
            (
                title,
                slug,
                summary,
                category_slug,
                technologies,
                repository_url,
                demo_url,
                source,
                status,
                is_open_source,
                is_featured,
                order,
            ) = row
            project, _ = Project.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "summary": summary,
                    "category": project_categories[category_slug],
                    "repository_url": repository_url,
                    "demo_url": demo_url,
                    "source": source,
                    "status": status,
                    "is_open_source": is_open_source,
                    "is_featured": is_featured,
                    "is_published": True,
                    "order": order,
                },
            )
            project.technologies.set([skills[name] for name in technologies if name in skills])

        for title, slug, summary, category_slug, order in data.MINI_PROJECTS:
            MiniProject.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "summary": summary,
                    # Demo links point at the public catalogue page.
                    "url": f"https://fgeeha.github.io/#{slug}",
                    "category": project_categories[category_slug],
                    "is_active": True,
                    "order": order,
                },
            )

        for name, url, username, order in data.SOCIAL_LINKS:
            SocialLink.objects.update_or_create(
                name=name,
                defaults={"url": url, "username": username, "order": order, "is_visible": True},
            )

        cat_name, cat_slug, cat_description, cat_order = data.BLOG_CATEGORY
        blog_category, _ = Category.objects.update_or_create(
            slug=cat_slug,
            defaults={"name": cat_name, "description": cat_description, "order": cat_order},
        )

        article_defaults = dict(data.ARTICLE)
        article_defaults.pop("slug")
        existing = Article.objects.filter(slug=data.ARTICLE["slug"]).first()
        Article.objects.update_or_create(
            slug=data.ARTICLE["slug"],
            defaults={
                **article_defaults,
                "category": blog_category,
                "status": ArticleStatus.PUBLISHED,
                # Keep the original publication date on re-runs.
                "published_at": (existing.published_at if existing else None) or timezone.now(),
            },
        )

        return {
            "Категории навыков": SkillCategory.objects.count(),
            "Навыки": Skill.objects.count(),
            "Проекты": Project.objects.count(),
            "Мини-проекты": MiniProject.objects.count(),
            "Социальные ссылки": SocialLink.objects.count(),
            "Статьи": Article.objects.count(),
        }
