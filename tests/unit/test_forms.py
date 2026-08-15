"""Contact form validation, including the honeypot trap."""

import pytest

from apps.contact.forms import ContactForm

pytestmark = pytest.mark.django_db

VALID = {
    "name": "Иван",
    "email": "ivan@example.com",
    "subject": "Вопрос по проекту",
    "message": "Здравствуйте, хочу обсудить сотрудничество.",
    "consent": "on",
}


def test_valid_payload_is_accepted():
    assert ContactForm(data=VALID).is_valid()


def test_subject_is_optional():
    payload = VALID | {"subject": ""}
    assert ContactForm(data=payload).is_valid()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", "И"),
        ("email", "not-an-email"),
        ("message", "коротко"),
        ("message", ""),
        ("name", ""),
    ],
)
def test_invalid_values_are_rejected(field, value):
    form = ContactForm(data=VALID | {field: value})
    assert not form.is_valid()
    assert field in form.errors


def test_honeypot_blocks_submission_without_naming_the_trap():
    form = ContactForm(data=VALID | {"website": "https://spam.example"})
    assert not form.is_valid()
    assert "website" not in form.errors
    assert form.non_field_errors()


def test_values_are_stripped():
    form = ContactForm(data=VALID | {"name": "  Иван  ", "message": "  Достаточно длинный текст  "})
    assert form.is_valid()
    assert form.cleaned_data["name"] == "Иван"
    assert form.cleaned_data["message"] == "Достаточно длинный текст"


def test_form_exposes_only_public_fields():
    # remote_addr / user_agent must never be settable by the client.
    assert set(ContactForm().fields) == {
        "website",
        "name",
        "email",
        "subject",
        "message",
        "consent",
    }


def test_consent_is_required():
    form = ContactForm(data=VALID | {"consent": ""})
    assert not form.is_valid()
    assert "consent" in form.errors


def test_consent_help_text_links_to_privacy_policy():
    form = ContactForm()
    assert 'href="/privacy/"' in form.fields["consent"].help_text
