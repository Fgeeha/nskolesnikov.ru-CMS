from django.contrib import admin
from django.db.models import Count, QuerySet
from django.http import HttpRequest

from apps.portfolio.models import (
    Certificate,
    DeveloperProfile,
    Education,
    Experience,
    MiniProject,
    Project,
    ProjectCategory,
    Skill,
    SkillCategory,
    SocialLink,
)


@admin.register(DeveloperProfile)
class DeveloperProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "headline", "is_available", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("full_name", "nickname", "headline", "avatar", "location")}),
        ("Тексты", {"fields": ("summary", "biography")}),
        ("Доступность", {"fields": ("is_available", "availability_note")}),
        ("Ссылки", {"fields": ("public_email", "resume_url", "cta_text", "cta_url")}),
        ("Служебное", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return not DeveloperProfile.objects.exists()


@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "skill_count")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")
    search_fields = ("name",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[SkillCategory]:
        # Annotated once for the whole page instead of a query per row.
        return super().get_queryset(request).annotate(_skill_count=Count("skills"))

    @admin.display(description="Навыков", ordering="_skill_count")
    def skill_count(self, obj: SkillCategory) -> int:
        # Attribute added by the annotation in get_queryset above.
        return getattr(obj, "_skill_count", 0)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "level", "is_featured", "order")
    list_filter = ("category", "is_featured")
    list_editable = ("is_featured", "order")
    search_fields = ("name",)
    ordering = ("category__order", "order", "name")
    autocomplete_fields = ("category",)


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("order", "name")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "status", "source", "is_featured", "is_published", "order")
    list_filter = ("status", "source", "category", "is_featured", "is_published", "is_open_source")
    list_editable = ("is_featured", "is_published", "order")
    search_fields = ("title", "summary", "description")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("category",)
    filter_horizontal = ("technologies",)
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "started_on"
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "description", "category")}),
        ("Изображение", {"fields": ("cover", "cover_alt")}),
        ("Ссылки", {"fields": ("repository_url", "demo_url", "source")}),
        (
            "Состояние",
            {
                "fields": (
                    "status",
                    "started_on",
                    "finished_on",
                    "is_open_source",
                    "is_featured",
                    "is_published",
                    "order",
                )
            },
        ),
        ("Технологии", {"fields": ("technologies",)}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
        ("Служебное", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def get_queryset(self, request: HttpRequest) -> QuerySet[Project]:
        return super().get_queryset(request).select_related("category")


@admin.register(MiniProject)
class MiniProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "url", "is_active", "order")
    list_filter = ("is_active", "category")
    list_editable = ("is_active", "order")
    search_fields = ("title", "summary")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("category",)


@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ("position", "organization", "started_on", "finished_on", "is_current", "order")
    list_filter = ("is_current",)
    search_fields = ("position", "organization")
    filter_horizontal = ("technologies",)
    ordering = ("order", "-started_on")


@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ("program", "institution", "degree", "started_on", "finished_on", "order")
    search_fields = ("program", "institution")
    ordering = ("order", "-started_on")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("title", "issuer", "issued_on", "order")
    search_fields = ("title", "issuer")
    ordering = ("order", "-issued_on")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("name", "username", "url", "is_visible", "order")
    list_editable = ("is_visible", "order")
    search_fields = ("name", "username")
    ordering = ("order", "name")
