"""django CMS plugin exposing recent published articles."""

from typing import Any

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from apps.blog.models import Article, LatestArticlesPluginModel


@plugin_pool.register_plugin
class LatestArticlesPlugin(CMSPluginBase):
    model = LatestArticlesPluginModel
    name = _("Последние статьи")
    module = _("Блог")
    render_template = "blog/plugins/latest_articles.html"
    cache = False

    def render(
        self, context: dict[str, Any], instance: LatestArticlesPluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        articles = Article.objects.published().with_related()
        if instance.category_id:
            articles = articles.filter(category_id=instance.category_id)
        context["articles"] = articles[: instance.limit]
        return context
