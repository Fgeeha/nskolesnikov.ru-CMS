"""RSS feed of published articles for readers and search engines.

Links are built from ``settings.SITE_URL`` rather than django.contrib.sites,
matching ``apps.core.templatetags.seo_tags`` — the ``django_site`` row is a
CMS dependency left at its default domain and isn't kept in sync.
"""

from django.conf import settings
from django.contrib.syndication.views import Feed
from django.db.models import QuerySet
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed

from apps.blog.models import Article
from apps.core.models import SiteSettings


class LatestArticlesFeed(Feed):
    feed_type = Rss201rev2Feed

    def title(self) -> str:
        return f"{SiteSettings.get_solo().site_name} — статьи"

    def link(self) -> str:
        return f"{settings.SITE_URL}{reverse('blog:article-list')}"

    def feed_url(self) -> str:
        # Without this, Django falls back to the django.contrib.sites domain
        # (unused elsewhere here, defaults to example.com) for the atom:link
        # self-reference.
        return f"{settings.SITE_URL}{reverse('blog:feed')}"

    def description(self) -> str:
        return (
            SiteSettings.get_solo().tagline
            or "Заметки о backend-разработке, AI/ML и инфраструктуре."
        )

    def items(self) -> QuerySet[Article]:
        return Article.objects.published().with_related()[:20]

    def item_title(self, item: Article) -> str:
        return item.title

    def item_description(self, item: Article) -> str:
        return item.excerpt

    def item_link(self, item: Article) -> str:
        return f"{settings.SITE_URL}{item.get_absolute_url()}"

    def item_pubdate(self, item: Article):
        return item.published_at

    def item_updateddate(self, item: Article):
        return item.updated_at

    def item_categories(self, item: Article) -> list[str]:
        return [item.category.name] if item.category else []
