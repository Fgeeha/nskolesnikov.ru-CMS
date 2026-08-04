"""Portfolio domain: profile, skills, projects, experience, education, links."""

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.core.models import OrderedModel, SeoModel, TimeStampedModel


class ProjectStatus(models.TextChoices):
    ACTIVE = "active", _("В разработке")
    COMPLETED = "completed", _("Завершён")
    ARCHIVED = "archived", _("Архив")


class ProjectSource(models.TextChoices):
    GITHUB = "github", "GitHub"
    GITVERSE = "gitverse", "GitVerse"
    OTHER = "other", _("Другое")


class DeveloperProfile(TimeStampedModel):
    """Public identity of the site owner. A single row is expected."""

    full_name = models.CharField(_("полное имя"), max_length=120)
    nickname = models.CharField(_("псевдоним"), max_length=60, blank=True)
    headline = models.CharField(_("специализация"), max_length=200)
    summary = models.TextField(_("краткое описание"), max_length=500)
    biography = models.TextField(_("расширенное описание"), blank=True)
    avatar = models.ImageField(_("фотография"), upload_to="profile/", blank=True)
    location = models.CharField(_("местоположение"), max_length=120, blank=True)
    is_available = models.BooleanField(_("открыт к предложениям"), default=True)
    availability_note = models.CharField(_("комментарий о доступности"), max_length=160, blank=True)
    resume_url = models.URLField(_("ссылка на резюме"), blank=True)
    public_email = models.EmailField(_("публичный email"), blank=True)
    cta_text = models.CharField(_("текст призыва к действию"), max_length=120, blank=True)
    cta_url = models.CharField(_("ссылка призыва к действию"), max_length=200, blank=True)

    class Meta:
        verbose_name = _("профиль разработчика")
        verbose_name_plural = _("профиль разработчика")

    def __str__(self) -> str:
        return self.full_name

    def clean(self) -> None:
        if not self.pk and DeveloperProfile.objects.exists():
            raise ValidationError(_("Профиль уже создан, отредактируйте существующий."))

    @property
    def display_name(self) -> str:
        return f"{self.full_name} ({self.nickname})" if self.nickname else self.full_name


class SkillCategory(OrderedModel):
    name = models.CharField(_("название"), max_length=80, unique=True)
    slug = models.SlugField(_("slug"), max_length=80, unique=True)

    class Meta:
        verbose_name = _("категория навыков")
        verbose_name_plural = _("категории навыков")
        ordering = ("order", "name")

    def __str__(self) -> str:
        return self.name


class SkillQuerySet(models.QuerySet["Skill"]):
    def featured(self) -> "SkillQuerySet":
        return self.filter(is_featured=True)


class Skill(OrderedModel):
    name = models.CharField(_("название"), max_length=80)
    category = models.ForeignKey(
        SkillCategory,
        verbose_name=_("категория"),
        on_delete=models.CASCADE,
        related_name="skills",
    )
    icon = models.CharField(
        _("иконка"),
        max_length=60,
        blank=True,
        help_text=_("Имя иконки из набора проекта, необязательно."),
    )
    level = models.CharField(
        _("уровень"),
        max_length=60,
        blank=True,
        help_text=_("Свободная характеристика, например «продакшн» или «базовый»."),
    )
    is_featured = models.BooleanField(_("показывать на главной"), default=False)

    objects = SkillQuerySet.as_manager()

    class Meta:
        verbose_name = _("навык")
        verbose_name_plural = _("навыки")
        ordering = ("category__order", "order", "name")
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="unique_skill_per_category"),
        ]

    def __str__(self) -> str:
        return self.name


class ProjectCategory(OrderedModel):
    name = models.CharField(_("название"), max_length=80, unique=True)
    slug = models.SlugField(_("slug"), max_length=80, unique=True)
    description = models.CharField(_("описание"), max_length=200, blank=True)

    class Meta:
        verbose_name = _("категория проектов")
        verbose_name_plural = _("категории проектов")
        ordering = ("order", "name")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("portfolio:project-list") + f"?category={self.slug}"


class ProjectQuerySet(models.QuerySet["Project"]):
    def published(self) -> "ProjectQuerySet":
        return self.filter(is_published=True)

    def featured(self) -> "ProjectQuerySet":
        return self.published().filter(is_featured=True)

    def with_related(self) -> "ProjectQuerySet":
        return self.select_related("category").prefetch_related("technologies__category")


class Project(OrderedModel, SeoModel, TimeStampedModel):
    title = models.CharField(_("название"), max_length=140)
    slug = models.SlugField(_("slug"), max_length=140, unique=True)
    summary = models.CharField(_("короткое описание"), max_length=280)
    description = models.TextField(_("полное описание"), blank=True)
    cover = models.ImageField(_("обложка"), upload_to="projects/", blank=True)
    cover_alt = models.CharField(_("alt-текст обложки"), max_length=160, blank=True)
    category = models.ForeignKey(
        ProjectCategory,
        verbose_name=_("категория"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
    technologies = models.ManyToManyField(
        Skill,
        verbose_name=_("технологии"),
        blank=True,
        related_name="projects",
    )
    repository_url = models.URLField(_("ссылка на репозиторий"), blank=True)
    demo_url = models.URLField(_("ссылка на демонстрацию"), blank=True)
    source = models.CharField(
        _("источник"),
        max_length=20,
        choices=ProjectSource.choices,
        default=ProjectSource.GITHUB,
    )
    status = models.CharField(
        _("статус"),
        max_length=20,
        choices=ProjectStatus.choices,
        default=ProjectStatus.ACTIVE,
        db_index=True,
    )
    started_on = models.DateField(_("дата начала"), null=True, blank=True)
    finished_on = models.DateField(_("дата завершения"), null=True, blank=True)
    is_open_source = models.BooleanField(_("open source"), default=True)
    is_featured = models.BooleanField(_("избранный"), default=False, db_index=True)
    is_published = models.BooleanField(_("опубликован"), default=True, db_index=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        verbose_name = _("проект")
        verbose_name_plural = _("проекты")
        ordering = ("order", "-started_on", "title")
        indexes = [
            models.Index(fields=["is_published", "is_featured"], name="project_pub_featured_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(finished_on__isnull=True)
                | Q(started_on__isnull=True)
                | Q(finished_on__gte=models.F("started_on")),
                name="project_finished_after_started",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("portfolio:project-detail", kwargs={"slug": self.slug})


class MiniProjectQuerySet(models.QuerySet["MiniProject"]):
    def active(self) -> "MiniProjectQuerySet":
        return self.filter(is_active=True)


class MiniProject(OrderedModel):
    """Small standalone web tools linked from the catalogue."""

    title = models.CharField(_("название"), max_length=120)
    slug = models.SlugField(_("slug"), max_length=120, unique=True)
    summary = models.CharField(_("краткое описание"), max_length=200)
    url = models.URLField(_("ссылка"))
    icon = models.CharField(_("иконка"), max_length=60, blank=True)
    category = models.ForeignKey(
        ProjectCategory,
        verbose_name=_("категория"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mini_projects",
    )
    is_active = models.BooleanField(_("активен"), default=True, db_index=True)

    objects = MiniProjectQuerySet.as_manager()

    class Meta:
        verbose_name = _("мини-проект")
        verbose_name_plural = _("мини-проекты")
        ordering = ("order", "title")

    def __str__(self) -> str:
        return self.title


class Experience(OrderedModel):
    organization = models.CharField(_("организация"), max_length=140)
    organization_url = models.URLField(_("сайт организации"), blank=True)
    position = models.CharField(_("должность"), max_length=140)
    description = models.TextField(_("описание"), blank=True)
    started_on = models.DateField(_("дата начала"))
    finished_on = models.DateField(_("дата окончания"), null=True, blank=True)
    is_current = models.BooleanField(_("текущее место работы"), default=False)
    technologies = models.ManyToManyField(
        Skill,
        verbose_name=_("технологии"),
        blank=True,
        related_name="experiences",
    )

    class Meta:
        verbose_name = _("опыт работы")
        verbose_name_plural = _("опыт работы")
        ordering = ("order", "-started_on")
        constraints = [
            models.CheckConstraint(
                condition=Q(finished_on__isnull=True) | Q(finished_on__gte=models.F("started_on")),
                name="experience_finished_after_started",
            ),
            models.CheckConstraint(
                condition=Q(is_current=False) | Q(finished_on__isnull=True),
                name="experience_current_has_no_end",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.position} — {self.organization}"


class Education(OrderedModel):
    institution = models.CharField(_("учебное заведение"), max_length=160)
    program = models.CharField(_("программа"), max_length=160)
    degree = models.CharField(_("степень"), max_length=120, blank=True)
    description = models.TextField(_("описание"), blank=True)
    started_on = models.DateField(_("дата начала"))
    finished_on = models.DateField(_("дата окончания"), null=True, blank=True)

    class Meta:
        verbose_name = _("образование")
        verbose_name_plural = _("образование")
        ordering = ("order", "-started_on")
        constraints = [
            models.CheckConstraint(
                condition=Q(finished_on__isnull=True) | Q(finished_on__gte=models.F("started_on")),
                name="education_finished_after_started",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.program} — {self.institution}"


class Certificate(OrderedModel):
    title = models.CharField(_("название"), max_length=180)
    issuer = models.CharField(_("организация"), max_length=160)
    issued_on = models.DateField(_("дата выдачи"))
    url = models.URLField(_("ссылка"), blank=True)

    class Meta:
        verbose_name = _("сертификат")
        verbose_name_plural = _("сертификаты")
        ordering = ("order", "-issued_on")

    def __str__(self) -> str:
        return self.title


class SocialLinkQuerySet(models.QuerySet["SocialLink"]):
    def visible(self) -> "SocialLinkQuerySet":
        return self.filter(is_visible=True)


class SocialLink(OrderedModel):
    name = models.CharField(_("название"), max_length=60, unique=True)
    url = models.URLField(_("ссылка"))
    icon = models.CharField(_("иконка"), max_length=60, blank=True)
    username = models.CharField(_("username"), max_length=80, blank=True)
    is_visible = models.BooleanField(_("отображать"), default=True)

    objects = SocialLinkQuerySet.as_manager()

    class Meta:
        verbose_name = _("социальная ссылка")
        verbose_name_plural = _("социальные ссылки")
        ordering = ("order", "name")

    def __str__(self) -> str:
        return self.name


# CMS plugin models live in a separate module for readability; importing them
# here keeps them discoverable by Django's app registry.
from apps.portfolio.plugin_models import (  # noqa: E402
    AboutPluginModel,
    EducationPluginModel,
    ExperiencePluginModel,
    FeaturedProjectsPluginModel,
    FeaturedSkillsPluginModel,
    HeroPluginModel,
    MiniProjectsPluginModel,
    SkillCategoriesPluginModel,
    SocialLinksPluginModel,
)

__all__ = [
    "AboutPluginModel",
    "Certificate",
    "DeveloperProfile",
    "Education",
    "EducationPluginModel",
    "Experience",
    "ExperiencePluginModel",
    "FeaturedProjectsPluginModel",
    "FeaturedSkillsPluginModel",
    "HeroPluginModel",
    "MiniProject",
    "MiniProjectsPluginModel",
    "Project",
    "ProjectCategory",
    "ProjectSource",
    "ProjectStatus",
    "Skill",
    "SkillCategoriesPluginModel",
    "SkillCategory",
    "SocialLink",
    "SocialLinksPluginModel",
]
