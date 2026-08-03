# syntax=docker/dockerfile:1

# --- Stage 1: dependencies ---------------------------------------------------
# Build tools and caches stay here and never reach the runtime image.
FROM python:3.13-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:0.9.2 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/opt/venv

WORKDIR /build

# Dependency layer is cached until the lock file itself changes.
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# --- Stage 2: dependencies including the development toolchain ---------------
FROM builder AS builder-dev

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

# --- Stage 3: common runtime base --------------------------------------------
FROM python:3.13-slim-bookworm AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app/src

# curl is needed by the container healthcheck and nothing else.
RUN apt-get update \
    && apt-get install --no-install-recommends -y curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system --gid 1001 app \
    && useradd --system --uid 1001 --gid app --create-home --home-dir /home/app app

WORKDIR /app

COPY --chown=app:app infra/docker/app/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R app:app /app/staticfiles /app/media

EXPOSE 8000

# Local check only: never depends on outbound internet access.
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD curl --fail --silent --show-error http://127.0.0.1:8000/health/ || exit 1

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# --- Stage 4: production ------------------------------------------------------
FROM base AS production

ENV DJANGO_SETTINGS_MODULE=config.settings.production

COPY --from=builder /opt/venv /opt/venv
COPY --chown=app:app pyproject.toml uv.lock ./
COPY --chown=app:app src ./src

USER app

# Worker count comes from WEB_CONCURRENCY, which gunicorn reads natively.
CMD ["gunicorn", "config.wsgi:application", \
     "--chdir", "/app/src", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "60", \
     "--graceful-timeout", "30", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]

# --- Stage 5: development -----------------------------------------------------
# Sources are bind-mounted by the development Compose file, so nothing is
# copied here beyond what the runtime already provides.
FROM base AS development

ENV DJANGO_SETTINGS_MODULE=config.settings.development \
    RUN_COLLECTSTATIC=0

COPY --from=builder-dev /opt/venv /opt/venv
COPY --chown=app:app pyproject.toml uv.lock ./
COPY --chown=app:app src ./src

USER app

CMD ["python", "/app/src/manage.py", "runserver", "0.0.0.0:8000"]
