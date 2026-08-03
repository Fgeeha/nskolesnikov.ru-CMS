"""Contact page: renders the form and stores submissions."""

import logging
import time
from typing import Any

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.contact.forms import ContactForm

logger = logging.getLogger(__name__)

LAST_SUBMIT_SESSION_KEY = "contact_last_submit_at"


def _seconds_since_last_submit(request: HttpRequest) -> float | None:
    last = request.session.get(LAST_SUBMIT_SESSION_KEY)
    if not isinstance(last, (int, float)):
        return None
    return time.time() - last


def _client_ip(request: HttpRequest) -> str | None:
    """Client address as seen behind the configured reverse proxy."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _notify(subject: str, body: str) -> None:
    if not settings.CONTACT_EMAIL:
        return
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        )
    except OSError:
        # Delivery problems must not lose the stored message.
        logger.exception("Contact notification could not be sent")


def contact(request: HttpRequest) -> HttpResponse:
    """Show and process the contact form."""
    cooldown = settings.CONTACT_RATE_LIMIT_SECONDS

    if request.method == "POST":
        elapsed = _seconds_since_last_submit(request)
        if cooldown and elapsed is not None and elapsed < cooldown:
            messages.error(request, "Сообщение уже отправлено. Подождите немного перед повтором.")
            return redirect(reverse("contact:contact"))

        form = ContactForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.remote_addr = _client_ip(request)
            message.user_agent = request.META.get("HTTP_USER_AGENT", "")[:300]
            message.save()
            request.session[LAST_SUBMIT_SESSION_KEY] = time.time()
            # Subject only: the message body may contain personal data.
            _notify(
                subject=f"Новое обращение с сайта: {message.subject or 'без темы'}",
                body=(
                    f"От: {message.name} <{message.email}>\n"
                    "Откройте админку, чтобы прочитать текст."
                ),
            )
            messages.success(request, "Сообщение отправлено. Отвечу в ближайшее время.")
            return redirect(reverse("contact:contact"))
    else:
        form = ContactForm()

    context: dict[str, Any] = {
        "form": form,
        "page_title": "Контакты",
        "meta_description": "Способы связи и форма обратной связи.",
    }
    return render(request, "contact/contact.html", context)
