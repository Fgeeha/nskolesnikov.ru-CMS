# nskolesnikov.ru

Персональный сайт-портфолио Python-разработчика на Django и django CMS.

Сайт представляет разработчика и его специализацию, показывает стек технологий,
избранные проекты, каталог небольших веб-инструментов, опыт работы, образование
и статьи. Содержимое редактируется через django CMS и Django Admin без изменения
исходного кода.

## Содержание

- [Стек](#стек)
- [Структура репозитория](#структура-репозитория)
- [Требования](#требования)
- [Быстрый старт через Docker](#быстрый-старт-через-docker)
- [Локальный запуск без Docker](#локальный-запуск-без-docker)
- [Переменные окружения](#переменные-окружения)
- [Команды разработки](#команды-разработки)
- [Проверки качества](#проверки-качества)
- [Production-развёртывание](#production-развёртывание)
- [Резервное копирование](#резервное-копирование)
- [Обновление зависимостей](#обновление-зависимостей)
- [Типичные проблемы](#типичные-проблемы)
- [Документация](#документация)

## Стек

| Слой | Технология |
|------|------------|
| Язык | Python 3.13 |
| Фреймворк | Django 5.2 |
| CMS | django CMS 5.0 LTS |
| База данных | PostgreSQL 17 |
| Сервер приложений | Gunicorn |
| Обратный прокси | Nginx |
| Медиатека | django-filer, easy-thumbnails |
| Окружение и зависимости | uv |
| Тесты | pytest, pytest-django |
| Качество кода | Ruff, mypy, django-stubs |
| Frontend | серверные шаблоны Django, собственный CSS, vanilla JS |

Frontend не использует SPA-фреймворки, Node.js и CDN.

## Структура репозитория

```text
.
├── src/                      Python-код проекта
│   ├── manage.py
│   ├── config/               настройки, urls, wsgi/asgi
│   │   └── settings/         base / development / production / test
│   ├── apps/
│   │   ├── core/             общая инфраструктура, SEO, health, sitemap
│   │   ├── portfolio/        профиль, навыки, проекты, опыт, образование
│   │   ├── blog/             статьи, категории, теги
│   │   └── contact/          контактная форма и обращения
│   ├── templates/            общие шаблоны и шаблоны CMS-плагинов
│   ├── static/               исходная статика (CSS, JS, иконки)
│   └── locale/               файлы переводов
├── tests/
│   ├── unit/
│   └── integration/
├── infra/
│   ├── docker/app/           Dockerfile приложения и entrypoint
│   ├── docker/nginx/         Dockerfile Nginx
│   ├── compose/              compose.dev.yml и compose.prod.yml
│   └── nginx/                шаблон конфигурации Nginx
└── docs/                     архитектура, развёртывание, работа с CMS
```

## Требования

- Docker 24+ и Docker Compose v2 — для запуска через контейнеры;
- либо `uv` 0.9+ и локальный PostgreSQL 17 — для запуска без Docker.

Установка `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Python устанавливать отдельно не нужно: версия зафиксирована в `.python-version`,
`uv` скачает её сам.

## Быстрый старт через Docker

```bash
cp .env.example .env

docker compose -f infra/compose/compose.dev.yml up --build
```

Сайт будет доступен на <http://localhost:8000>.

Миграции применяются автоматически при старте контейнера. Дальше нужно загрузить
демонстрационное содержимое и создать администратора:

```bash
docker compose -f infra/compose/compose.dev.yml exec web \
  python /app/src/manage.py seed_demo

docker compose -f infra/compose/compose.dev.yml exec web \
  python /app/src/manage.py createsuperuser
```

Команда `seed_demo` идемпотентна: повторный запуск обновляет существующие записи
и не создаёт дубликатов. Она же создаёт главную страницу django CMS и наполняет
её плейсхолдеры блоками.

Административная панель — <http://localhost:8000/admin/>.

Остановка (данные в volumes сохраняются):

```bash
docker compose -f infra/compose/compose.dev.yml down
```

## Локальный запуск без Docker

Нужен работающий PostgreSQL. Создайте базу и пользователя:

```sql
CREATE USER portfolio WITH PASSWORD 'portfolio';
CREATE DATABASE portfolio OWNER portfolio;
```

Затем:

```bash
cp .env.example .env
# в .env укажите POSTGRES_HOST=localhost

uv sync

uv run python src/manage.py migrate
uv run python src/manage.py seed_demo
uv run python src/manage.py createsuperuser
uv run python src/manage.py runserver
```

## Переменные окружения

Полный список с примерами — в `.env.example`. Файл `.env` в репозиторий не
попадает.

| Переменная | Назначение |
|------------|------------|
| `DJANGO_SETTINGS_MODULE` | модуль настроек: `config.settings.development` или `config.settings.production` |
| `DJANGO_SECRET_KEY` | секретный ключ; в production обязателен, fallback отсутствует |
| `DJANGO_DEBUG` | режим отладки, в production всегда выключен |
| `DJANGO_ALLOWED_HOSTS` | список доменов через запятую; в development можно оставить пустым — тогда хосты не проверяются, в production обязателен |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | доверенные origin для CSRF |
| `DJANGO_SITE_URL` | публичный абсолютный URL для canonical, sitemap и Open Graph |
| `DJANGO_TIME_ZONE` | часовой пояс, по умолчанию `Europe/Moscow` |
| `DJANGO_MEDIA_ROOT` | путь к пользовательским файлам |
| `POSTGRES_*` | параметры подключения к базе |
| `EMAIL_*`, `DEFAULT_FROM_EMAIL` | параметры SMTP |
| `CONTACT_EMAIL` | адрес для уведомлений о новых обращениях; пусто — уведомления выключены |
| `CONTACT_RATE_LIMIT_SECONDS` | минимальный интервал между отправками формы |
| `NGINX_SERVER_NAME` | `server_name` в конфигурации Nginx (production) |
| `HTTP_PORT` | внешний порт Nginx (production) |
| `GUNICORN_WORKERS` | число воркеров Gunicorn (production) |
| `TEST_POSTGRES_*`, `TEST_DATABASE_URL` | параметры тестовой базы |

`.env` в корне репозитория — единственный источник настроек: его читают и
приложение, и оба Compose-файла. Значения из блока `environment` в Compose
всегда перекрывают `env_file`, поэтому там оставлено только то, что обязано
отличаться внутри контейнера (`POSTGRES_HOST=db`, модуль настроек, путь к
media).

Сгенерировать секретный ключ:

```bash
uv run python -c "import secrets; print(secrets.token_urlsafe(64))"
```

## Команды разработки

`Makefile` — тонкая оболочка над `uv run` и Docker Compose:

```bash
make help              # список команд

make install           # uv sync
make lock              # uv lock
make run               # runserver
make migrate           # применить миграции
make migrations        # создать миграции
make superuser         # создать администратора
make seed              # демонстрационные данные

make test              # pytest на PostgreSQL (база поднимается сама)
make test-cov          # то же с отчётом о покрытии
make test-db-up        # поднять тестовую базу отдельно
make test-db-down      # остановить тестовую базу
make lint              # ruff check + ruff format --check
make format            # ruff check --fix + ruff format
make typecheck         # mypy
make check             # django check
make cms-check         # django CMS check
make verify            # все проверки подряд

make compose-up        # dev-стек в Docker
make compose-down      # остановить dev-стек
make compose-logs      # логи приложения

make prod-up           # production-стек
make prod-down         # остановить production-стек
make prod-logs         # логи production
```

## Проверки качества

```bash
uv lock --check
uv sync --frozen
make test-db-up
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run python src/manage.py check
uv run python src/manage.py cms check
uv run python src/manage.py makemigrations --check --dry-run
uv run pytest
```

Тесты идут на PostgreSQL — на том же движке, что и production, поэтому
ограничения базы и поведение транзакций проверяются по-настоящему. Нужен
отдельный одноразовый контейнер:

```bash
make test-db-up      # PostgreSQL на 127.0.0.1:55432, данные в tmpfs
uv run pytest
make test-db-down    # когда база больше не нужна
```

`make test` и `make test-cov` поднимают его сами. Тесты не обращаются в сеть.

Чтобы использовать другую базу, задайте строку подключения целиком:

```bash
TEST_DATABASE_URL=postgres://user:pass@localhost:5432/portfolio uv run pytest
```

Команды `check`, `cms check` и `makemigrations --check` требуют доступной базы.
Локально удобнее запускать их внутри dev-контейнера:

```bash
docker compose -f infra/compose/compose.dev.yml exec web \
  python /app/src/manage.py cms check
```

## Production-развёртывание

Кратко; подробности — в [`docs/deployment.md`](docs/deployment.md).

```bash
# на сервере
cp .env.example .env
# заполните .env: реальный SECRET_KEY, домен, пароль базы, SMTP

docker compose --env-file .env -f infra/compose/compose.prod.yml up -d --build

docker compose --env-file .env -f infra/compose/compose.prod.yml exec web \
  python /app/src/manage.py createsuperuser
```

Флаг `--env-file .env` нужен production-стеку: из него берутся значения,
которые Compose подставляет ещё при разборе файла — `HTTP_PORT` и
`NGINX_SERVER_NAME`. Development-стеку он не требуется.

Production-стек состоит из `db`, `web` и `nginx`. Миграции и `collectstatic`
выполняются в entrypoint при старте контейнера. Порт PostgreSQL наружу не
публикуется.

Проверка конфигурации перед выкладкой:

```bash
docker compose -f infra/compose/compose.prod.yml exec web \
  python /app/src/manage.py check --deploy
```

TLS в этом compose не терминируется: предполагается внешний прокси или
дополнительный слой (например, Caddy или Traefik). Если TLS ещё не настроен,
временно выставьте `DJANGO_SECURE_SSL_REDIRECT=false`, иначе браузер получит
цикл редиректов.

## Резервное копирование

База данных:

```bash
docker compose -f infra/compose/compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
  > backup-$(date +%F).sql
```

Восстановление:

```bash
docker compose -f infra/compose/compose.prod.yml exec -T db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < backup-2026-01-01.sql
```

Медиафайлы:

```bash
docker run --rm \
  -v nskolesnikov-prod_media_data:/data:ro \
  -v "$(pwd)":/backup \
  alpine tar czf /backup/media-$(date +%F).tar.gz -C /data .
```

Дампы и архивы не коммитятся: они исключены в `.gitignore`.

## Обновление зависимостей

```bash
uv add package-name          # добавить
uv add --dev package-name    # добавить в dev-группу
uv remove package-name       # удалить
uv lock --upgrade            # обновить версии в lock-файле
uv sync                      # применить

make verify                  # прогнать все проверки
```

`uv.lock` вручную не редактируется. `pyproject.toml` и `uv.lock` коммитятся
вместе.

## Типичные проблемы

**`/` отдаёт 302 на `/admin/cms/pagecontent/`**
Главная страница django CMS не создана. Выполните `seed_demo` или создайте
страницу в админке и отметьте её как домашнюю.

**`ConfirmationOfVersion4Required` при миграции**
Не задан `CMS_CONFIRM_VERSION4`. В проекте он включён в
`src/config/settings/base.py`; ошибка означает, что используется другой модуль
настроек.

**`ImproperlyConfigured: Set the DJANGO_SECRET_KEY environment variable`**
Production-настройки намеренно не имеют небезопасных значений по умолчанию.
Заполните `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS`,
`DJANGO_CSRF_TRUSTED_ORIGINS` и `DJANGO_SITE_URL`.

**Бесконечный редирект на production**
`DJANGO_SECURE_SSL_REDIRECT=true` без работающего TLS. Настройте TLS или
временно выключите редирект.

**Статика не отдаётся на production**
`collectstatic` выполняется в entrypoint. Проверьте, что переменная
`RUN_COLLECTSTATIC` не выставлена в `0` и что volume `static_data` смонтирован в
оба сервиса — `web` и `nginx`.

**`Bad Request (400)` или `DisallowedHost` после смены домена или при заходе по IP**
Домен или адрес не указан в `DJANGO_ALLOWED_HOSTS`. В development переменную
можно просто оставить пустой — тогда проверка хостов отключается и сайт
открывается по IP машины в локальной сети.

Если переменная задана в `.env`, но не применяется, проверьте, что она не
продублирована в блоке `environment` соответствующего Compose-файла: значения
оттуда всегда перекрывают `env_file`.

**`password authentication failed for user` после смены `POSTGRES_PASSWORD`**
PostgreSQL применяет `POSTGRES_PASSWORD` только при первой инициализации
volume. Смените пароль в уже существующей базе:

```bash
docker compose -f infra/compose/compose.dev.yml exec db \
  psql -U portfolio -d postgres -c "ALTER USER portfolio WITH PASSWORD 'новый-пароль';"
```

## Документация

- [`docs/architecture.md`](docs/architecture.md) — структура приложений, модели, решения;
- [`docs/deployment.md`](docs/deployment.md) — развёртывание на VPS, обновление, откат;
- [`docs/content-management.md`](docs/content-management.md) — работа с django CMS и админкой.

## Лицензия

MIT — см. [LICENSE](LICENSE).
