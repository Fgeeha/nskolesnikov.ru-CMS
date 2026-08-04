"""Sitemap definitions. Drafts and unpublished objects are excluded."""

import datetime

from cms.sitemaps import CMSSitemap
from django.contrib.sitemaps import Sitemap
from django.db.models import QuerySet
from django.urls import reverse

from apps.blog.models import Article
from apps.portfolio.models import Project


class StaticViewSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6
    i18n = False

    def items(self) -> list[str]:
        return [
            "portfolio:about",
            "portfolio:project-list",
            "portfolio:mini-project-list",
            "portfolio:resume",
            "blog:article-list",
            "contact:contact",
        ]

    def location(self, item: str) -> str:
        return reverse(item)


class ProjectSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self) -> QuerySet[Project]:
        return Project.objects.published()

    def lastmod(self, obj: Project) -> datetime.datetime:
        return obj.updated_at


class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self) -> QuerySet[Article]:
        return Article.objects.published()

    def lastmod(self, obj: Article) -> datetime.datetime:
        return obj.updated_at


SITEMAPS = {
    # CMSSitemap only lists published page contents, drafts stay out.
    "cms": CMSSitemap,
    "static": StaticViewSitemap,
    "projects": ProjectSitemap,
    "articles": ArticleSitemap,
}
