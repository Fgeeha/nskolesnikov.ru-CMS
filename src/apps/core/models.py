"""Shared abstract models and site-wide settings."""

from cms.models import CMSPlugin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Adds creation and update timestamps."""

    created_at = models.DateTimeField(_("создано"), auto_now_add=True)
    updated_at = models.DateTimeField(_("обновлено"), auto_now=True)

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    """Adds a manual sort position, lowest first."""

    order = models.PositiveIntegerField(_("порядок"), default=0, db_index=True)

    class Meta:
        abstract = True


class SeoModel(models.Model):
    """Per-object SEO overrides; empty fields fall back to the object itself."""

    seo_title = models.CharField(_("SEO title"), max_length=70, blank=True)
    seo_description = models.CharField(_("SEO description"), max_length=200, blank=True)

    class Meta:
        abstract = True


class SiteSettings(models.Model):
    """Singleton holding site-wide identity and SEO defaults."""

    site_name = models.CharField(_("название сайта"), max_length=120, default="Никита Колесников")
    tagline = models.CharField(_("подзаголовок"), max_length=200, blank=True)
    default_seo_title = models.CharField(_("SEO title по умолчанию"), max_length=70, blank=True)
    default_seo_description = models.CharField(
        _("SEO description по умолчанию"), max_length=200, blank=True
    )
    default_og_image = models.ImageField(_("изображение Open Graph"), upload_to="site/", blank=True)
    footer_text = models.CharField(_("текст в подвале"), max_length=200, blank=True)
    robots_extra = models.TextField(
        _("дополнительные строки robots.txt"),
        blank=True,
        help_text=_("Добавляются в конец сгенерированного robots.txt."),
    )
    yandex_verification = models.CharField(_("Yandex verification"), max_length=64, blank=True)
    google_verification = models.CharField(_("Google verification"), max_length=64, blank=True)

    class Meta:
        verbose_name = _("настройки сайта")
        verbose_name_plural = _("настройки сайта")

    def __str__(self) -> str:
        return self.site_name

    def clean(self) -> None:
        if not self.pk and SiteSettings.objects.exists():
            raise ValidationError(_("Настройки сайта уже созданы, отредактируйте существующие."))

    @classmethod
    def get_solo(cls) -> "SiteSettings":
        """Return the singleton, or unsaved defaults when it does not exist yet.

        Nothing is written here: this runs on every GET request through the
        context processor.
        """
        return cls.objects.first() or cls()


class SectionPluginBase(CMSPlugin):
    """Shared heading fields for every section-style CMS plugin."""

    heading = models.CharField(_("заголовок"), max_length=120, blank=True)
    subheading = models.CharField(_("подзаголовок"), max_length=240, blank=True)
    anchor = models.SlugField(
        _("якорь"),
        max_length=60,
        blank=True,
        help_text=_("Используется как id секции для навигации по странице."),
    )

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.heading or str(self._meta.verbose_name)


class CtaPluginModel(SectionPluginBase):
    """Standalone call-to-action band."""

    text = models.TextField(_("текст"), max_length=400, blank=True)
    button_label = models.CharField(_("текст кнопки"), max_length=60)
    button_url = models.CharField(_("ссылка кнопки"), max_length=200)
    secondary_label = models.CharField(_("текст второй кнопки"), max_length=60, blank=True)
    secondary_url = models.CharField(_("ссылка второй кнопки"), max_length=200, blank=True)

    class Meta:
        verbose_name = _("блок призыва к действию")
