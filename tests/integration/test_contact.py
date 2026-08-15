"""Contact page: submission, storage, notification and abuse protection."""

import pytest
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from apps.contact.models import ContactMessage

pytestmark = pytest.mark.django_db

PAYLOAD = {
    "name": "Иван",
    "email": "ivan@example.com",
    "subject": "Сотрудничество",
    "message": "Здравствуйте, хочу обсудить проект.",
    "website": "",
    "consent": "on",
}


def url() -> str:
    return reverse("contact:contact")


def test_get_renders_form(client, content):
    response = client.get(url())
    assert response.status_code == 200
    assert "csrfmiddlewaretoken" in response.content.decode()


def test_get_does_not_create_messages(client, content):
    client.get(url())
    assert ContactMessage.objects.count() == 0


def test_valid_post_stores_message_and_redirects(client, content):
    response = client.post(url(), PAYLOAD)
    assert response.status_code == 302
    assert response.url == url()

    message = ContactMessage.objects.get()
    assert message.name == "Иван"
    assert message.email == "ivan@example.com"
    assert message.is_processed is False
    assert message.consent is True


def test_missing_consent_is_rejected_without_storing(client, content):
    response = client.post(url(), PAYLOAD | {"consent": ""})
    assert response.status_code == 200
    assert ContactMessage.objects.count() == 0


def test_notification_email_is_sent_without_message_body(client, content):
    client.post(url(), PAYLOAD)
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["owner@example.com"]
    assert PAYLOAD["message"] not in mail.outbox[0].body


@override_settings(CONTACT_EMAIL="")
def test_no_notification_when_recipient_is_unset(client, content):
    client.post(url(), PAYLOAD)
    assert ContactMessage.objects.count() == 1
    assert mail.outbox == []


def test_invalid_post_is_rerendered_without_storing(client, content):
    response = client.post(url(), PAYLOAD | {"email": "broken"})
    assert response.status_code == 200
    assert ContactMessage.objects.count() == 0


def test_honeypot_submission_is_discarded(client, content):
    response = client.post(url(), PAYLOAD | {"website": "https://spam.example"})
    assert response.status_code == 200
    assert ContactMessage.objects.count() == 0


@override_settings(CONTACT_RATE_LIMIT_SECONDS=600)
def test_repeat_submission_is_rate_limited(client, content):
    client.post(url(), PAYLOAD)
    response = client.post(url(), PAYLOAD | {"subject": "Повтор"})
    assert response.status_code == 302
    assert ContactMessage.objects.count() == 1


def test_client_metadata_is_recorded(client, content):
    client.post(url(), PAYLOAD, HTTP_USER_AGENT="pytest-agent")
    message = ContactMessage.objects.get()
    assert message.user_agent == "pytest-agent"
    assert message.remote_addr
