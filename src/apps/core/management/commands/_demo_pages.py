"""Idempotent creation of the CMS page tree and the home page composition."""

import logging
from typing import Any

from cms.api import add_plugin, create_page
from cms.models import Page, PageContent, Placeholder

logger = logging.getLogger(__name__)

HOME_SLUG = "home"
LANGUAGE = "ru"

# (placeholder slot, plugin type, plugin data)
HOME_PLUGINS: list[tuple[str, str, dict[str, Any]]] = [
    (
        "hero",
        "HeroPlugin",
        {
            "primary_label": "Смотреть проекты",
            "primary_url": "/projects/",
            "secondary_label": "Связаться",
            "secondary_url": "/contacts/",
            "terminal_command": "whoami",
        },
    ),
    (
        "sections",
        "AboutPlugin",
        {"heading": "Обо мне", "anchor": "about", "text_source": "biography"},
    ),
    (
        "sections",
        "FeaturedSkillsPlugin",
        {"heading": "Основной стек", "anchor": "stack", "limit": 16},
    ),
    (
        "sections",
        "FeaturedProjectsPlugin",
        {"heading": "Избранные проекты", "anchor": "projects", "limit": 6},
    ),
    (
        "sections",
        "SkillCategoriesPlugin",
        {"heading": "Технологии", "anchor": "skills"},
    ),
    (
        "sections",
        "MiniProjectsPlugin",
        {"heading": "Мини-проекты", "anchor": "tools", "limit": 8},
    ),
    (
        "sections",
        "LatestArticlesPlugin",
        {"heading": "Последние статьи", "anchor": "blog", "limit": 3},
    ),
    (
        "closing",
        "ContactBlockPlugin",
        {
            "heading": "Связаться",
            "anchor": "contact",
            "text": "Расскажите о задаче — отвечу в течение пары дней.",
            "show_form": True,
        },
    ),
]


def seed_home_page(created_by: str = "seed_demo") -> str:
    """Create the home page once and fill its placeholders.

    Re-running leaves an existing page untouched: editors' changes to the
    composition must survive a repeated seed.
    """
    if Page.objects.filter(is_home=True).exists():
        return "Главная страница уже существует, состав блоков не изменялся."

    page = create_page(
        title="Главная",
        template="cms/home.html",
        language=LANGUAGE,
        slug=HOME_SLUG,
        menu_title="Главная",
        in_navigation=True,
        created_by=created_by,
    )
    # Without this the page stays at /home/ and "/" has nothing to serve.
    page.set_as_homepage()

    content = PageContent.admin_manager.filter(page=page, language=LANGUAGE).first()
    if content is None:
        return "Страница создана, но контент для языка не найден — блоки не добавлены."

    content.rescan_placeholders()
    placeholders = {ph.slot: ph for ph in Placeholder.objects.get_for_obj(content)}

    added = 0
    for slot, plugin_type, plugin_data in HOME_PLUGINS:
        placeholder = placeholders.get(slot)
        if placeholder is None:
            logger.warning("Placeholder %r is missing in cms/home.html", slot)
            continue
        add_plugin(placeholder, plugin_type, LANGUAGE, **plugin_data)
        added += 1

    return f"Главная страница создана, добавлено блоков: {added}."
