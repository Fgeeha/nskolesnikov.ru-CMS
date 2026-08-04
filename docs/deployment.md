# Развёртывание

Развёртывание на VPS через Docker Compose.

## Состав production-стека

| Сервис | Образ | Назначение |
|--------|-------|------------|
| `db` | `postgres:17-alpine` | база данных, порт наружу не публикуется |
| `web` | сборка `infra/docker/app/Dockerfile`, стадия `production` | Gunicorn + Django |
| `nginx` | сборка `infra/docker/nginx/Dockerfile` | статика, media, обратный прокси |

Volumes: `postgres_data`, `static_data`, `media_data`. Они переживают
пересборку контейнеров.

## Требования к серверу

- Linux с Docker 24+ и Docker Compose v2;
- 1 vCPU и 2 GB RAM достаточно для персонального сайта;
- открытые порты 80 и 443 (443 — если TLS терминируется на этом же хосте);
- домен, указывающий A-записью на сервер.

## Первое развёртывание

```bash
git clone <repository-url> nskolesnikov.ru
cd nskolesnikov.ru

cp .env.example .env
```

Заполните `.env`:

```dotenv
DJANGO_SETTINGS_MODULE=config.settings.production
DJANGO_SECRET_KEY=<длинная случайная строка>
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=example.com,www.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
DJANGO_SITE_URL=https://example.com

POSTGRES_DB=portfolio
POSTGRES_USER=portfolio
POSTGRES_PASSWORD=<надёжный пароль>
POSTGRES_HOST=db
POSTGRES_PORT=5432

NGINX_SERVER_NAME=example.com www.example.com
HTTP_PORT=80
GUNICORN_WORKERS=3

EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=<логин>
EMAIL_HOST_PASSWORD=<пароль>
EMAIL_USE_TLS=true
DEFAULT_FROM_EMAIL=noreply@example.com
CONTACT_EMAIL=owner@example.com
```

Сгенерировать ключ:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(64))"
```

Запуск:

```bash
docker compose --env-file .env -f infra/compose/compose.prod.yml up -d --build
```

`--env-file .env` обязателен: из этого файла Compose берёт `HTTP_PORT` и
`NGINX_SERVER_NAME` ещё на этапе разбора конфигурации. Остальные переменные
попадают в контейнеры через `env_file` того же файла.

Entrypoint дожидается PostgreSQL, применяет миграции и выполняет
`collectstatic`. Проверьте состояние:

```bash
docker compose --env-file .env -f infra/compose/compose.prod.yml ps
docker compose --env-file .env -f infra/compose/compose.prod.yml logs -f web
```

Все три контейнера должны быть в состоянии `healthy`.

Создайте администратора:

```bash
docker compose --env-file .env -f infra/compose/compose.prod.yml exec web \
  python /app/src/manage.py createsuperuser
```

Суперпользователь намеренно не создаётся автоматически: пароль по умолчанию —
это открытая дверь.

Загрузите начальное содержимое, если нужно:

```bash
docker compose --env-file .env -f infra/compose/compose.prod.yml exec web \
  python /app/src/manage.py seed_demo
```

## TLS

`compose.prod.yml` слушает только HTTP. Варианты:

**1. Внешний обратный прокси на хосте** (Caddy, Traefik, системный Nginx с
Certbot). Прокси терминирует TLS и передаёт заголовок `X-Forwarded-Proto`;
Django настроен его читать через `SECURE_PROXY_SSL_HEADER`. Установите
`HTTP_PORT=8080` и проксируйте на него.

**2. Certbot рядом со стеком.** Добавьте сервис с `certbot/certbot`, смонтируйте
общий volume для сертификатов и расширьте шаблон
`infra/nginx/default.conf.template` блоком `listen 443 ssl`.

До настройки TLS выставьте `DJANGO_SECURE_SSL_REDIRECT=false` — иначе Django
будет бесконечно редиректить на HTTPS, которого нет.

## Проверка перед выкладкой

```bash
docker compose --env-file .env -f infra/compose/compose.prod.yml exec web \
  python /app/src/manage.py check --deploy
```

Ожидаемый результат — `System check identified no issues (1 silenced)`.
Заглушена только `security.W019`: django CMS требует
`X_FRAME_OPTIONS="SAMEORIGIN"` для своих редакторов.

Дополнительно:

```bash
curl -f https://example.com/health/
curl -s https://example.com/robots.txt
curl -s https://example.com/sitemap.xml | head -20
```

## Обновление

```bash
cd nskolesnikov.ru
git pull

# перед обновлением — резервная копия
docker compose --env-file .env -f infra/compose/compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
  > "backup-$(date +%F-%H%M).sql"

docker compose --env-file .env -f infra/compose/compose.prod.yml up -d --build
```

Миграции применяются автоматически. Простой ограничен временем пересборки и
перезапуска контейнера `web`.

Если в обновлении есть необратимая миграция (удаление поля или таблицы),
проверьте её на копии базы до выкладки.

## Откат

```bash
git checkout <предыдущий-тег-или-коммит>
docker compose --env-file .env -f infra/compose/compose.prod.yml up -d --build
```

Откат кода не откатывает применённые миграции. Если новая версия добавила
несовместимые изменения схемы, восстановите базу из резервной копии:

```bash
docker compose --env-file .env -f infra/compose/compose.prod.yml stop web
docker compose --env-file .env -f infra/compose/compose.prod.yml exec -T db \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < backup-2026-01-01-1200.sql
docker compose --env-file .env -f infra/compose/compose.prod.yml start web
```

## Резервное копирование

### База данных

```bash
docker compose --env-file .env -f infra/compose/compose.prod.yml exec -T db \
  pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists \
  | gzip > "backup-$(date +%F).sql.gz"
```

Ежедневно через cron:

```cron
0 3 * * * cd /srv/nskolesnikov.ru && docker compose --env-file .env -f infra/compose/compose.prod.yml exec -T db pg_dump -U portfolio -d portfolio --clean --if-exists | gzip > /srv/backups/db-$(date +\%F).sql.gz
```

### Медиафайлы

```bash
docker run --rm \
  -v nskolesnikov-prod_media_data:/data:ro \
  -v /srv/backups:/backup \
  alpine tar czf "/backup/media-$(date +%F).tar.gz" -C /data .
```

Восстановление медиа:

```bash
docker run --rm \
  -v nskolesnikov-prod_media_data:/data \
  -v /srv/backups:/backup \
  alpine sh -c "tar xzf /backup/media-2026-01-01.tar.gz -C /data"
```

Обе операции собраны в скрипте:

```bash
infra/scripts/backup.sh /srv/backups
```

Резервные копии храните вне сервера приложения. Каталог `backups/` исключён из
Git.

## Эксплуатация

```bash
# состояние
docker compose --env-file .env -f infra/compose/compose.prod.yml ps

# логи
docker compose --env-file .env -f infra/compose/compose.prod.yml logs -f web
docker compose --env-file .env -f infra/compose/compose.prod.yml logs -f nginx

# консоль Django
docker compose --env-file .env -f infra/compose/compose.prod.yml exec web \
  python /app/src/manage.py shell

# перезапуск только приложения
docker compose --env-file .env -f infra/compose/compose.prod.yml restart web

# остановка (volumes сохраняются)
docker compose --env-file .env -f infra/compose/compose.prod.yml down
```

`docker compose down -v` удаляет volumes вместе с базой и медиафайлами.
Не выполняйте эту команду без осознанного намерения стереть данные.

## Мониторинг

Endpoint `/health/` возвращает `200` с `{"status": "ok", "database": "ok"}` и
`503`, если база недоступна. Ответ не кешируется и подходит для внешнего
мониторинга и для healthcheck контейнера.

## Диагностика

**Контейнер `web` перезапускается по кругу**
`docker compose --env-file .env -f infra/compose/compose.prod.yml logs web`. Частая причина —
незаполненная обязательная переменная окружения: production-настройки падают
сразу, а не работают с небезопасным значением.

**502 от Nginx**
Контейнер `web` не поднялся или ещё не прошёл healthcheck. Проверьте `ps` и
логи.

**Статика отдаёт 404**
`collectstatic` не выполнился или volume `static_data` не смонтирован в оба
сервиса. Проверьте:

```bash
docker compose --env-file .env -f infra/compose/compose.prod.yml exec nginx ls /var/www/static
```

**`Bad Request (400)`**
Домен не указан в `DJANGO_ALLOWED_HOSTS`.

**CSRF-ошибка при отправке формы**
Домен не указан в `DJANGO_CSRF_TRUSTED_ORIGINS`, обязательно со схемой
`https://`.
