"""Generic presentation plugins that carry no domain data."""

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from apps.core.models import CtaPluginModel


@plugin_pool.register_plugin
class CtaPlugin(CMSPluginBase):
    model = CtaPluginModel
    name = _("Призыв к действию")
    module = _("Общее")
    render_template = "core/plugins/cta.html"
