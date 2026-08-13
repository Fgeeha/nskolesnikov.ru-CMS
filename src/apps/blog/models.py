"""Blog domain: categories, tags and articles with draft/published states."""

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from djangocms_text.fields import HTMLField

from apps.core.models import OrderedModel, SectionPluginBase, SeoModel, TimeStampedModel


class ArticleStatus(models.TextChoices):
    DRAFT = "draft", _("Черновик")
    PUBLISHED = "published", _("Опубликована")


class Category(OrderedModel):
    name = models.CharField(_("название"), max_length=80, unique=True)
    slug = models.SlugField(_("slug"), max_length=80, unique=True)
    description = models.CharField(_("описание"), max_length=200, blank=True)

    class Meta:
        verbose_name = _("категория статей")
        verbose_name_plural = _("категории статей")
        ordering = ("order", "name")

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("blog:category", kwargs={"slug": self.slug})


class Tag(models.Model):
    name = models.CharField(_("название"), max_length=60, unique=True)
    slug = models.SlugField(_("slug"), max_length=60, unique=True)

    class Meta:
        verbose_name = _("тег")
        verbose_name_plural = _("теги")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("blog:tag", kwargs={"slug": self.slug})


class ArticleQuerySet(models.QuerySet["Article"]):
    def published(self) -> "ArticleQuerySet":
        """Articles visible to anonymous visitors."""
        return self.filter(
            status=ArticleStatus.PUBLISHED,
            published_at__isnull=False,
            published_at__lte=timezone.now(),
        )

    def with_related(self) -> "ArticleQuerySet":
        return self.select_related("category").prefetch_related("tags")


class Article(SeoModel, TimeStampedModel):
    title = models.CharField(_("заголовок"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=200, unique=True)
    excerpt = models.TextField(_("превью"), max_length=400)
    body = HTMLField(_("текст статьи"))
    cover = models.ImageField(_("обложка"), upload_to="articles/", blank=True)
    cover_alt = models.CharField(_("alt-текст обложки"), max_length=160, blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name=_("категория"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    tags = models.ManyToManyField(Tag, verbose_name=_("теги"), blank=True, related_name="articles")
    status = models.CharField(
        _("статус"),
        max_length=20,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField(_("дата публикации"), null=True, blank=True, db_index=True)
    reading_time = models.PositiveSmallIntegerField(
        _("время чтения, мин"),
        default=0,
        help_text=_("0 — рассчитывается автоматически при отображении."),
    )

    objects = ArticleQuerySet.as_manager()

    class Meta:
        verbose_name = _("статья")
        verbose_name_plural = _("статьи")
        ordering = ("-published_at", "-created_at")
        indexes = [
            models.Index(fields=["status", "published_at"], name="article_status_pub_idx"),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("blog:article-detail", kwargs={"slug": self.slug})

    @property
    def is_published(self) -> bool:
        return (
            self.status == ArticleStatus.PUBLISHED
            and self.published_at is not None
            and self.published_at <= timezone.now()
        )

    @property
    def estimated_reading_time(self) -> int:
        """Reading time in minutes; the stored value wins when set."""
        if self.reading_time:
            return self.reading_time
        words = len(strip_tags(self.body).split())
        return max(1, round(words / 180))


class LatestArticlesPluginModel(SectionPluginBase):
    """Recent published articles, optionally limited to one category."""

    category = models.ForeignKey(
        Category,
        verbose_name=_("категория"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    limit = models.PositiveSmallIntegerField(_("максимум статей"), default=3)
    show_all_link = models.BooleanField(_("ссылка на все статьи"), default=True)

    class Meta:
        verbose_name = _("блок последних статей")
