from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from apps.contact.models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    # Message bodies and client metadata stay off the list view on purpose.
    list_display = ("name", "email", "subject", "is_processed", "created_at")
    list_filter = ("is_processed", "created_at")
    search_fields = ("name", "email", "subject")
    readonly_fields = (
        "name",
        "email",
        "subject",
        "message",
        "remote_addr",
        "user_agent",
        "created_at",
        "updated_at",
    )
    date_hierarchy = "created_at"
    actions = ("mark_processed",)
    fieldsets = (
        (None, {"fields": ("name", "email", "subject", "message")}),
        ("Обработка", {"fields": ("is_processed",)}),
        (
            "Служебное",
            {
                "fields": ("remote_addr", "user_agent", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        # Messages arrive only through the public form.
        return False

    @admin.action(description="Отметить как обработанные")
    def mark_processed(self, request: HttpRequest, queryset: QuerySet[ContactMessage]) -> None:
        queryset.update(is_processed=True)
