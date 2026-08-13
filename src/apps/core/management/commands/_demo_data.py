"""Demonstration content for `seed_demo`, kept out of the command body."""

SITE_SETTINGS = {
    "site_name": "Никита Колесников",
    "tagline": "Python / Go разработчик — backend, AI/ML, DevOps",
    "default_seo_title": "Никита Колесников — Python / Go разработчик",
    "default_seo_description": (
        "Backend-разработчик: Python, Go, RAG-системы на своей инфраструктуре, "
        "чат-боты, edge AI и мониторинг."
    ),
    "footer_text": "Открытые проекты, заметки и инструменты.",
}

PROFILE = {
    "full_name": "Никита Колесников",
    "nickname": "fgeeha",
    "headline": "Python / Go Developer — Backend, AI/ML, DevOps",
    "summary": (
        "Разрабатываю backend-сервисы на Python и Go: RAG-системы в закрытом контуре, "
        "чат-боты, edge AI и инструменты мониторинга."
    ),
    "biography": (
        "Backend-разработчик с фокусом на Python и Go. Основные направления — "
        "RAG-системы на собственной инфраструктуре, интеграция локальных LLM, "
        "телеграм- и MAX-боты, edge AI на устройствах с ограниченными ресурсами.\n\n"
        "Отдельная часть работы — DevOps: контейнеризация, CI/CD в GitHub Actions "
        "и Gitea Actions, сканирование образов на уязвимости, экспорт метрик в "
        "Prometheus и построение дашбордов в Grafana.\n\n"
        "Веду открытые репозитории: библиотеки, шаблоны сервисов, утилиты и "
        "небольшие браузерные инструменты."
    ),
    "location": "Россия",
    "is_available": True,
    "availability_note": "Открыт к предложениям",
    "public_email": "kolesnikov.nikitavlg@gmail.com",
    "cta_text": "Обсудить проект",
    "cta_url": "/contacts/",
}

SKILL_CATEGORIES = [
    ("Языки", "languages", 10),
    ("Backend", "backend", 20),
    ("AI/ML", "ai-ml", 30),
    ("Базы данных", "databases", 40),
    ("DevOps", "devops", 50),
    ("Мониторинг", "monitoring", 60),
    ("GUI", "gui", 70),
]

# (name, category slug, level, featured, order)
SKILLS = [
    ("Python", "languages", "основной", True, 10),
    ("Go", "languages", "продакшн", True, 20),
    ("PHP", "languages", "поддержка", False, 30),
    ("Bash", "languages", "скрипты", False, 40),
    ("Django", "backend", "основной", True, 10),
    ("FastAPI", "backend", "продакшн", True, 20),
    ("Flask", "backend", "", False, 30),
    ("aiogram", "backend", "боты", True, 40),
    ("RAG", "ai-ml", "основной", True, 10),
    ("LangChain", "ai-ml", "", True, 20),
    ("Ollama", "ai-ml", "локальные LLM", True, 30),
    ("ChromaDB", "ai-ml", "векторный поиск", False, 40),
    ("PyTorch", "ai-ml", "", True, 50),
    ("Keras", "ai-ml", "", False, 60),
    ("pandas", "ai-ml", "", False, 70),
    ("numpy", "ai-ml", "", False, 80),
    ("PostgreSQL", "databases", "основная", True, 10),
    ("SQL", "databases", "", False, 20),
    ("MySQL", "databases", "", False, 30),
    ("Alembic", "databases", "миграции", False, 40),
    ("Docker", "devops", "ежедневно", True, 10),
    ("Git", "devops", "", True, 20),
    ("Linux", "devops", "", True, 30),
    ("GitHub Actions", "devops", "CI/CD", True, 40),
    ("Gitea Actions", "devops", "CI/CD", False, 50),
    ("Trivy", "devops", "безопасность", False, 60),
    ("Prometheus", "monitoring", "", True, 10),
    ("Grafana", "monitoring", "", True, 20),
    ("PyQt6", "gui", "", False, 10),
    ("tkinter", "gui", "", False, 20),
    ("Fyne", "gui", "Go", False, 30),
]

PROJECT_CATEGORIES = [
    ("AI и данные", "ai", "RAG-системы, локальные модели и обработка данных.", 10),
    ("Боты и интеграции", "bots", "Чат-боты и интеграции с мессенджерами.", 20),
    ("Инфраструктура", "infra", "DevOps-инструменты, мониторинг и безопасность.", 30),
    ("Утилиты", "tools", "Настольные и командные утилиты.", 40),
]

# (title, slug, summary, category slug, techs, repo, demo, source, status,
#  open source, featured, order)
PROJECTS = [
    (
        "ROoP — RAG on-premises",
        "roop",
        "RAG-система для работы с документами полностью в закрытом контуре.",
        "ai",
        ["Python", "Django", "RAG", "Ollama", "ChromaDB"],
        "https://github.com/Fgeeha/ROoP",
        "",
        "github",
        "active",
        True,
        True,
        10,
    ),
    (
        "Edge AI Plant Diagnostics",
        "edge-ai-plant-diagnostics",
        "Диагностика болезней растений на edge-устройствах, проект SEDM-2026.",
        "ai",
        ["Python", "PyTorch"],
        "https://github.com/Fgeeha/sedm2026-edge-ai-plant-diagnostics",
        "",
        "github",
        "active",
        True,
        True,
        20,
    ),
    (
        "Полка под контролем",
        "shelf-control",
        "Пайплайн распознавания ценников для Lenta Tech Life Hack 2026.",
        "ai",
        ["Python", "PyTorch"],
        "https://github.com/Fgeeha/Lenta-Tech-Life-Hack-2026",
        "https://huggingface.co/spaces/fgeeha/shelf-control",
        "github",
        "completed",
        True,
        True,
        30,
    ),
    (
        "MAX Action",
        "max-action",
        "GitHub Action для отправки уведомлений в мессенджер MAX.",
        "infra",
        ["Go", "Docker"],
        "https://github.com/Fgeeha/max-action",
        "",
        "github",
        "completed",
        True,
        True,
        40,
    ),
    (
        "Tg-ollama",
        "tg-ollama",
        "Telegram-бот с потоковой выдачей ответов локальной модели Ollama.",
        "bots",
        ["Python", "Ollama", "aiogram"],
        "https://github.com/Fgeeha/Tg-ollama",
        "",
        "github",
        "active",
        True,
        True,
        50,
    ),
    (
        "MAX Bot Template",
        "max-bot-template",
        "Шаблон бота с rate limiting, graceful shutdown и готовым CI/CD.",
        "bots",
        ["Python", "Docker", "GitHub Actions"],
        "https://github.com/Fgeeha/template-max-bot-github-gitea",
        "",
        "github",
        "completed",
        True,
        False,
        60,
    ),
    (
        "rocm-smi-exporter",
        "rocm-smi-exporter",
        "Экспортер метрик видеокарт AMD в Prometheus.",
        "infra",
        ["Python", "Prometheus", "Grafana"],
        "https://github.com/Fgeeha/rocm-smi-exporter",
        "",
        "github",
        "completed",
        True,
        True,
        70,
    ),
    (
        "monitor-dir",
        "monitor-dir",
        "Контроль целостности файлов с экспортом метрик в Prometheus.",
        "infra",
        ["Python", "Docker", "Prometheus"],
        "https://gitverse.ru/nkolesnikov/monitor-dir",
        "",
        "gitverse",
        "active",
        True,
        False,
        80,
    ),
    (
        "vuln-scanner",
        "vuln-scanner",
        "Сканирование контейнерных образов на известные уязвимости.",
        "infra",
        ["Bash", "Docker", "Trivy"],
        "https://github.com/Fgeeha/vuln-scanner",
        "",
        "github",
        "completed",
        True,
        False,
        90,
    ),
    (
        "Divoom Timegate PC Info",
        "divoom-timegate-pc-info",
        "Кроссплатформенный монитор состояния ПК для Divoom Times Gate.",
        "tools",
        ["Python"],
        "https://github.com/Fgeeha/Divoom-Timegate-PC-Info",
        "",
        "github",
        "completed",
        True,
        False,
        100,
    ),
    (
        "Stress Tester",
        "stress-tester",
        "Нагрузочное тестирование CPU и RAM с графическим интерфейсом.",
        "tools",
        ["Go", "Fyne"],
        "https://github.com/Fgeeha/stress-tester",
        "",
        "github",
        "completed",
        True,
        False,
        110,
    ),
    (
        "Fast-Chat-Auth",
        "fast-chat-auth",
        "Чат с аутентификацией по JWT на FastAPI.",
        "bots",
        ["Python", "FastAPI"],
        "https://github.com/Fgeeha/Fast-Chat-Auth",
        "",
        "github",
        "completed",
        True,
        False,
        120,
    ),
]

# (title, slug, summary, url, category slug, order)
MINI_PROJECTS = [
    ("Password Generator", "password-generator", "Генератор паролей в браузере.", "tools", 10),
    ("JSON Formatter", "json-formatter", "Форматирование и проверка JSON.", "tools", 20),
    ("Base64 Tool", "base64-tool", "Кодирование и декодирование Base64.", "tools", 30),
    ("UUID Generator", "uuid-generator", "Генерация UUID разных версий.", "tools", 40),
    ("Contrast Checker", "contrast-checker", "Проверка контрастности по WCAG.", "tools", 50),
    ("OG Preview", "og-preview", "Предпросмотр Open Graph-карточек.", "tools", 60),
    ("QR Generator", "qr-generator", "Генерация QR-кодов.", "tools", 70),
    ("Text Diff", "text-diff", "Сравнение двух текстов.", "tools", 80),
    ("CSV Editor", "csv-editor", "Правка CSV прямо в браузере.", "tools", 90),
    (
        "File Encoding Identifier",
        "file-encoding-identifier",
        "Определение кодировки файла.",
        "tools",
        100,
    ),
    ("Image Compressor", "image-compressor", "Сжатие изображений без сервера.", "tools", 110),
    ("World Clock", "world-clock", "Часы нескольких часовых поясов.", "tools", 120),
    ("Work Day Timer", "work-day-timer", "Таймер рабочего дня.", "tools", 130),
    ("Typing Test", "typing-test", "Тест скорости печати.", "tools", 140),
    ("Sort Visualizer", "sort-visualizer", "Визуализация алгоритмов сортировки.", "tools", 150),
    ("Game of Life", "game-of-life", "Игра «Жизнь» Конвея.", "tools", 160),
]

# (name, url, username, order)
SOCIAL_LINKS = [
    ("GitHub", "https://github.com/Fgeeha", "@Fgeeha", 10),
    ("GitVerse", "https://gitverse.ru/nkolesnikov", "nkolesnikov", 20),
    ("Telegram", "https://t.me/fgeeha", "@FgeeHa", 30),
    (
        "LinkedIn",
        "https://www.linkedin.com/in/nikita-kolesnikov-337b78323/",
        "Nikita Kolesnikov",
        40,
    ),
]

BLOG_CATEGORY = ("Инженерия", "engineering", "Заметки о разработке и эксплуатации.", 10)

ARTICLE = {
    "title": "RAG в закрытом контуре: что ломается первым",
    "slug": "rag-on-premises-first-failures",
    "excerpt": (
        "Практические выводы после сборки RAG-системы без доступа в интернет: "
        "выбор эмбеддингов, размер чанка и цена неудачного ретривера."
    ),
    "body": (
        "<p>Когда RAG собирается в закрытом контуре, привычные компромиссы меняются. "
        "Нельзя дёрнуть внешний API, нельзя опереться на чужие эмбеддинги — всё "
        "работает на своём железе, и любое лишнее звено сразу видно в latency.</p>"
        "<h2>Ретривер ломается первым</h2>"
        "<p>Модель отвечает связно и уверенно даже на нерелевантном контексте, "
        "поэтому качество поиска приходится измерять отдельно, до подключения LLM.</p>"
        "<h2>Нарезка документов</h2>"
        "<p>Второй частый источник проблем — нарезка документов. Фиксированный размер "
        "чанка разрывает таблицы и списки, а именно они чаще всего содержат ответ. "
        "Разметка по структуре документа даёт больше, чем подбор длины окна.</p>"
        "<h2>Наблюдаемость</h2>"
        "<p>Без логов запросов и метрик попадания в контекст система превращается "
        "в чёрный ящик, который невозможно улучшать осознанно.</p>"
    ),
    "reading_time": 4,
    "seo_title": "RAG в закрытом контуре: практические выводы",
    "seo_description": (
        "Что ломается первым при сборке on-premises RAG: ретривер, нарезка "
        "документов и наблюдаемость."
    ),
}
