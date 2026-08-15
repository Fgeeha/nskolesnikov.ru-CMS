.DEFAULT_GOAL := help

MANAGE := uv run python src/manage.py
DEV_COMPOSE := docker compose -f infra/compose/compose.dev.yml
PROD_COMPOSE := docker compose --env-file .env -f infra/compose/compose.prod.yml
TEST_COMPOSE := docker compose -f infra/compose/compose.test.yml

.PHONY: help install lock run migrate migrations superuser seed \
        test test-cov test-db-up test-db-down \
        lint format typecheck check cms-check migration-check verify \
        up-local down-local logs shell \
        up-prod down-prod logs-prod clean

help: ## Показать список целей
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# --- Окружение -----------------------------------------------------------------
.env: ## Создать .env из примера, если его нет
	@test -f .env || (cp .env.example .env && echo "Создан .env из .env.example — заполните значения")

install: ## Установить окружение из uv.lock
	uv sync

lock: ## Пересобрать uv.lock
	uv lock

# --- Django ----------------------------------------------------------------------
run: ## Запустить сервер разработки
	$(MANAGE) runserver

migrate: ## Применить миграции
	$(MANAGE) migrate

migrations: ## Создать миграции для приложений проекта
	$(MANAGE) makemigrations core portfolio blog contact

superuser: ## Создать суперпользователя (интерактивно)
	$(MANAGE) createsuperuser

seed: ## Загрузить демонстрационный контент (идемпотентно)
	$(MANAGE) seed_demo

# --- Проверки --------------------------------------------------------------------
test-db-up: ## Поднять одноразовый PostgreSQL для тестов
	$(TEST_COMPOSE) up -d --wait

test-db-down: ## Остановить тестовый PostgreSQL
	$(TEST_COMPOSE) down

test: test-db-up ## Прогнать тесты против PostgreSQL
	uv run pytest

test-cov: test-db-up ## Прогнать тесты с отчётом покрытия
	uv run pytest --cov

lint: ## Проверить код (ruff check + ruff format --check)
	uv run ruff check .
	uv run ruff format --check .

format: ## Отформатировать код (ruff check --fix + ruff format)
	uv run ruff check . --fix
	uv run ruff format .

typecheck: ## Проверить типы (mypy)
	uv run mypy src

check: ## Django system checks (manage.py check)
	$(MANAGE) check

cms-check: ## Проверки конфигурации django CMS
	$(MANAGE) cms check

migration-check: ## Упасть, если есть непримененные изменения моделей
	$(MANAGE) makemigrations --check --dry-run

verify: lint typecheck check cms-check migration-check test ## Прогнать все проверки перед коммитом

# --- Docker: разработка -----------------------------------------------------------
up-local: .env ## Собрать и поднять dev-стек
	$(DEV_COMPOSE) up --build

down-local: ## Остановить dev-стек (тома сохраняются)
	$(DEV_COMPOSE) down

logs: ## Логи dev-приложения (follow)
	$(DEV_COMPOSE) logs -f web

shell: ## Shell внутри контейнера dev-приложения
	$(DEV_COMPOSE) exec web sh

# --- Docker: прод -------------------------------------------------------------------
up-prod: .env ## Собрать и поднять прод-стек (detached)
	$(PROD_COMPOSE) up -d --build

down-prod: ## Остановить прод-стек (тома сохраняются)
	$(PROD_COMPOSE) down

logs-prod: ## Логи прод-стека (follow)
	$(PROD_COMPOSE) logs -f

# --- Обслуживание --------------------------------------------------------------------
clean: ## Удалить локальные кэши и артефакты сборки
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov staticfiles
	find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} +
