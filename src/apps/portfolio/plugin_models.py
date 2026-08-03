"""CMS plugin models for the portfolio app.

Plugins never duplicate domain data: they store presentation parameters and,
where useful, an explicit selection of existing objects.
"""

from cms.models import CMSPlugin
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.core.models import SectionPluginBase


class HeroPluginModel(CMSPlugin):
    """Opening block. Text falls back to the developer profile when empty."""

    title = models.CharField(_("заголовок"), max_length=140, blank=True)
    subtitle = models.CharField(_("подзаголовок"), max_length=240, blank=True)
    intro = models.TextField(_("вступительный текст"), max_length=600, blank=True)
    show_terminal = models.BooleanField(_("показывать терминал"), default=True)
    terminal_command = models.CharField(_("команда в терминале"), max_length=80, default="whoami")
    primary_label = models.CharField(_("текст основной кнопки"), max_length=60, blank=True)
    primary_url = models.CharField(_("ссылка основной кнопки"), max_length=200, blank=True)
    secondary_label = models.CharField(_("текст второй кнопки"), max_length=60, blank=True)
    secondary_url = models.CharField(_("ссылка второй кнопки"), max_length=200, blank=True)

    class Meta:
        verbose_name = _("блок Hero")

    def __str__(self) -> str:
        return self.title or "Hero"


class AboutPluginModel(SectionPluginBase):
    """«Обо мне» block rendered from the developer profile."""

    class TextSource(models.TextChoices):
        SUMMARY = "summary", _("Краткое описание")
        BIOGRAPHY = "biography", _("Расширенное описание")

    text_source = models.CharField(
        _("источник текста"),
        max_length=20,
        choices=TextSource.choices,
        default=TextSource.BIOGRAPHY,
    )
    show_avatar = models.BooleanField(_("показывать фотографию"), default=True)
    show_facts = models.BooleanField(_("показывать блок фактов"), default=True)

    class Meta:
        verbose_name = _("блок «Обо мне»")


class SkillCategoriesPluginModel(SectionPluginBase):
    """Skills grouped by category."""

    categories = models.ManyToManyField(
        "portfolio.SkillCategory",
        verbose_name=_("категории"),
        blank=True,
        related_name="+",
        help_text=_("Пусто — показываются все категории."),
    )

    class Meta:
        verbose_name = _("блок категорий навыков")

    def copy_relations(self, oldinstance: "SkillCategoriesPluginModel") -> None:
        """Carry the M2M selection over when the plugin is copied.

        django CMS copies plain fields itself but leaves M2M relations empty,
        which would silently reset the selection on every page copy.
        """
        self.categories.set(oldinstance.categories.all())


class FeaturedSkillsPluginModel(SectionPluginBase):
    """Flat grid of skills marked as featured."""

    limit = models.PositiveSmallIntegerField(_("максимум навыков"), default=16)
    show_level = models.BooleanField(_("показывать уровень"), default=False)

    class Meta:
        verbose_name = _("сетка избранных навыков")


class FeaturedProjectsPluginModel(SectionPluginBase):
    """Selected projects, optionally narrowed to one category."""

    category = models.ForeignKey(
        "portfolio.ProjectCategory",
        verbose_name=_("категория"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    limit = models.PositiveSmallIntegerField(_("максимум проектов"), default=6)
    only_featured = models.BooleanField(_("только избранные"), default=True)
    show_all_link = models.BooleanField(_("ссылка на все проекты"), default=True)

    class Meta:
        verbose_name = _("блок избранных проектов")


class MiniProjectsPluginModel(SectionPluginBase):
    """Compact list of small browser tools."""

    limit = models.PositiveSmallIntegerField(_("максимум мини-проектов"), default=12)
    show_all_link = models.BooleanField(_("ссылка на все мини-проекты"), default=True)

    class Meta:
        verbose_name = _("блок мини-проектов")


class ExperiencePluginModel(SectionPluginBase):
    """Work experience timeline."""

    limit = models.PositiveSmallIntegerField(_("максимум записей"), default=5)
    show_technologies = models.BooleanField(_("показывать технологии"), default=True)

    class Meta:
        verbose_name = _("блок опыта работы")


class EducationPluginModel(SectionPluginBase):
    """Education timeline."""

    limit = models.PositiveSmallIntegerField(_("максимум записей"), default=5)
    show_certificates = models.BooleanField(_("показывать сертификаты"), default=False)

    class Meta:
        verbose_name = _("блок образования")


class SocialLinksPluginModel(SectionPluginBase):
    """Social profiles row."""

    class Style(models.TextChoices):
        ICONS = "icons", _("Только иконки")
        CARDS = "cards", _("Карточки")

    style = models.CharField(
        _("оформление"), max_length=10, choices=Style.choices, default=Style.CARDS
    )

    class Meta:
        verbose_name = _("блок социальных ссылок")
