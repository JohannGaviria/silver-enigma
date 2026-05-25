PYTHON=python3

EXCLUDE=.venv venv
EXCLUDE_REGEX=$(shell echo $(EXCLUDE) | sed 's/ /|/g')
EXCLUDE_COMMA=$(shell echo $(EXCLUDE) | sed 's/ /,/g')

# Colors for output
GREEN=\033[0;32m
BLUE=\033[0;34m
YELLOW=\033[1;33m
RED=\033[0;31m
NC=\033[0m # No Color

.PHONY: help setup format lint test pre-commit install up down check

help: ## Show this help message
	@echo "$(YELLOW)=== Available Commands ===$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-16s$(NC) %s\n", $$1, $$2}'

setup: ## Install development dependencies and git hooks
	poetry install
	pre-commit install

up: ## Start docker containers with build
	docker compose up --build

down: ## Stop docker containers
	docker compose down

test: ## Run tests with pytest
	@echo "$(BLUE)Running tests...$(NC)"
	pytest -v

test-coverage: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	poetry run pytest --cov=src/ --cov-fail-under=70

format: ## Format and auto-fix code
	@echo "$(BLUE)Fixing lint issues...$(NC)"
	poetry run ruff check --fix .
	@echo "$(BLUE)Formatting code...$(NC)"
	poetry run ruff format .

lint: ## Lint + type checking
	@echo "$(BLUE)Running Ruff lint...$(NC)"
	poetry run ruff check .
	@echo "$(BLUE)Running mypy...$(NC)"
	poetry run mypy .

check: ## Check without modifying
	@echo "$(BLUE)Checking formatting...$(NC)"
	poetry run ruff format --check .
	@echo "$(BLUE)Checking lint...$(NC)"
	poetry run ruff check .
	@echo "$(BLUE)Checking types...$(NC)"
	poetry run mypy .

pre-commit: ## Run all hooks
	poetry run pre-commit run --all-files
