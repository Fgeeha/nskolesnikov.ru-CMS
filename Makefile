.DEFAULT_GOAL := help

MANAGE := uv run python src/manage.py
DEV_COMPOSE := docker compose -f infra/compose/compose.dev.yml
PROD_COMPOSE := docker compose --env-file .env -f infra/compose/compose.prod.yml
TEST_COMPOSE := docker compose -f infra/compose/compose.test.yml

.PHONY: help install lock run migrate migrations superuser seed \
        test test-cov test-db-up test-db-down \
        lint format typecheck check cms-check migration-check verify \
        compose-up compose-down compose-logs compose-shell \
        prod-up prod-down prod-logs clean

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

# --- Environment -------------------------------------------------------------
.env: ## Create .env from the example when it is missing
	@test -f .env || (cp .env.example .env && echo "Создан .env из .env.example — заполните значения")

install: ## Sync the virtual environment from uv.lock
	uv sync

lock: ## Refresh uv.lock
	uv lock

# --- Django ------------------------------------------------------------------
run: ## Start the development server
	$(MANAGE) runserver

migrate: ## Apply migrations
	$(MANAGE) migrate

migrations: ## Create migrations for the project apps
	$(MANAGE) makemigrations core portfolio blog contact

superuser: ## Create a superuser interactively
	$(MANAGE) createsuperuser

seed: ## Load demonstration content (idempotent)
	$(MANAGE) seed_demo

# --- Quality -----------------------------------------------------------------
test-db-up: ## Start the throwaway PostgreSQL used by the test suite
	$(TEST_COMPOSE) up -d --wait

test-db-down: ## Stop the test PostgreSQL
	$(TEST_COMPOSE) down

test: test-db-up ## Run the test suite against PostgreSQL
	uv run pytest

test-cov: test-db-up ## Run the test suite with a coverage report
	uv run pytest --cov

lint: ## Lint with Ruff
	uv run ruff check .
	uv run ruff format --check .

format: ## Auto-format and auto-fix with Ruff
	uv run ruff check . --fix
	uv run ruff format .

typecheck: ## Type-check with mypy
	uv run mypy src

check: ## Run Django system checks
	$(MANAGE) check

cms-check: ## Run django CMS configuration checks
	$(MANAGE) cms check

migration-check: ## Fail if models have unapplied migration changes
	$(MANAGE) makemigrations --check --dry-run

verify: lint typecheck check cms-check migration-check test ## Run every quality gate

# --- Docker: development -----------------------------------------------------
compose-up: .env ## Build and start the development stack
	$(DEV_COMPOSE) up --build

compose-down: ## Stop the development stack (volumes are preserved)
	$(DEV_COMPOSE) down

compose-logs: ## Follow the development application logs
	$(DEV_COMPOSE) logs -f web

compose-shell: ## Open a shell inside the development application container
	$(DEV_COMPOSE) exec web sh

# --- Docker: production ------------------------------------------------------
prod-up: .env ## Build and start the production stack in the background
	$(PROD_COMPOSE) up -d --build

prod-down: ## Stop the production stack (volumes are preserved)
	$(PROD_COMPOSE) down

prod-logs: ## Follow the production logs
	$(PROD_COMPOSE) logs -f

# --- Housekeeping ------------------------------------------------------------
clean: ## Remove local caches and build artefacts
	rm -rf .pytest_cache .ruff_cache .mypy_cache .coverage htmlcov staticfiles
	find . -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} +
