"""Contact form with server-side validation and a honeypot."""

from typing import Any

from django import forms
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.contact.models import ContactMessage


class ContactForm(forms.ModelForm):
    """Public contact form.

    Spam protection is deliberately dependency-free: a hidden honeypot field
    plus a session-based cooldown enforced in the view.
    """

    # Bots fill every field they find; humans never see this one.
    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={"autocomplete": "off", "tabindex": "-1", "aria-hidden": "true"}
        ),
    )
    # Not a model form field: kept declared explicitly so it is always
    # required regardless of the underlying BooleanField's default, and so
    # the link target is resolved at request time, not at import time.
    consent = forms.BooleanField(
        required=True,
        label=_("Даю согласие на обработку персональных данных"),
        error_messages={"required": _("Необходимо согласие на обработку персональных данных.")},
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields["consent"].help_text = format_html(
            'Ознакомьтесь с <a href="{}" target="_blank" rel="noopener noreferrer">'
            "политикой обработки персональных данных</a>.",
            reverse("core:privacy"),
        )

    def save(self, commit: bool = True) -> ContactMessage:
        instance: ContactMessage = super().save(commit=False)
        instance.consent = self.cleaned_data["consent"]
        if commit:
            instance.save()
        return instance

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name", "maxlength": 120}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "subject": forms.TextInput(attrs={"maxlength": 160}),
            "message": forms.Textarea(attrs={"rows": 6, "maxlength": 4000}),
        }
        labels = {
            "name": _("Имя"),
            "email": _("Email"),
            "subject": _("Тема"),
            "message": _("Сообщение"),
        }

    def clean_name(self) -> str:
        name: str = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError(_("Укажите имя длиной не менее двух символов."))
        return name

    def clean_message(self) -> str:
        message: str = self.cleaned_data["message"].strip()
        if len(message) < 10:
            raise forms.ValidationError(_("Опишите вопрос подробнее — не менее 10 символов."))
        return message

    def clean_subject(self) -> str:
        subject: str = self.cleaned_data.get("subject", "").strip()
        return subject

    def clean(self) -> dict[str, Any]:
        cleaned: dict[str, Any] = super().clean() or {}
        if cleaned.get("website"):
            # Do not reveal the trap; report a generic failure.
            raise forms.ValidationError(_("Не удалось отправить сообщение. Попробуйте ещё раз."))
        return cleaned
