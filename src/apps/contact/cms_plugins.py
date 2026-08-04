"""django CMS plugin rendering the contact section."""

from typing import Any

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from apps.contact.forms import ContactForm
from apps.contact.models import ContactBlockPluginModel
from apps.portfolio.models import DeveloperProfile, SocialLink


@plugin_pool.register_plugin
class ContactBlockPlugin(CMSPluginBase):
    model = ContactBlockPluginModel
    name = _("Контактный блок")
    module = _("Контакты")
    render_template = "contact/plugins/contact_block.html"
    cache = False

    def render(
        self, context: dict[str, Any], instance: ContactBlockPluginModel, placeholder: str
    ) -> dict[str, Any]:
        context = super().render(context, instance, placeholder)
        # The embedded form posts to the dedicated contact view, which owns
        # validation, rate limiting and notification.
        context["form"] = ContactForm() if instance.show_form else None
        context["links"] = SocialLink.objects.visible() if instance.show_social else []
        context["profile"] = DeveloperProfile.objects.first() if instance.show_email else None
        return context
