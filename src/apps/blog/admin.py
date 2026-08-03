from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils import timezone

from apps.blog.models import Article, ArticleStatus, Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("order", "name")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "published_at", "updated_at")
    list_filter = ("status", "category", "tags")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("category",)
    filter_horizontal = ("tags",)
    date_hierarchy = "published_at"
    readonly_fields = ("created_at", "updated_at")
    actions = ("publish_articles", "unpublish_articles")
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "tags")}),
        ("Содержание", {"fields": ("excerpt", "body", "reading_time")}),
        ("Обложка", {"fields": ("cover", "cover_alt")}),
        ("Публикация", {"fields": ("status", "published_at")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
        ("Служебное", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Article]:
        return super().get_queryset(request).select_related("category")

    @admin.action(description="Опубликовать выбранные статьи")
    def publish_articles(self, request: HttpRequest, queryset: QuerySet[Article]) -> None:
        now = timezone.now()
        for article in queryset:
            article.status = ArticleStatus.PUBLISHED
            if article.published_at is None:
                article.published_at = now
            article.save(update_fields=["status", "published_at", "updated_at"])

    @admin.action(description="Снять с публикации")
    def unpublish_articles(self, request: HttpRequest, queryset: QuerySet[Article]) -> None:
        queryset.update(status=ArticleStatus.DRAFT)
