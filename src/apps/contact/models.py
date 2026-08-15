"""Contact messages submitted through the public form."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import SectionPluginBase, TimeStampedModel


class ContactMessage(TimeStampedModel):
    name = models.CharField(_("имя"), max_length=120)
    email = models.EmailField(_("email"))
    subject = models.CharField(_("тема"), max_length=160, blank=True)
    message = models.TextField(_("сообщение"), max_length=4000)
    consent = models.BooleanField(_("согласие на обработку персональных данных"), default=False)
    is_processed = models.BooleanField(_("обработано"), default=False, db_index=True)
    # Kept for abuse handling only; never rendered in list views.
    remote_addr = models.GenericIPAddressField(_("IP-адрес"), null=True, blank=True)
    user_agent = models.CharField(_("User-Agent"), max_length=300, blank=True)

    class Meta:
        verbose_name = _("обращение")
        verbose_name_plural = _("обращения")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["is_processed", "-created_at"], name="contact_processed_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"


class ContactBlockPluginModel(SectionPluginBase):
    """Contact section: intro text, social links and an optional form."""

    text = models.TextField(_("текст"), max_length=400, blank=True)
    show_form = models.BooleanField(_("показывать форму"), default=True)
    show_social = models.BooleanField(_("показывать социальные ссылки"), default=True)
    show_email = models.BooleanField(_("показывать email"), default=True)

    class Meta:
        verbose_name = _("контактный блок")
