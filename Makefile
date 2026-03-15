.PHONY: help install dev run test test-unit test-integration test-e2e lint format typecheck migrate migrate-create docker-up docker-down

help:
	@echo "Available commands:"
	@echo "  install          Install production dependencies"
	@echo "  dev              Install all dependencies (including dev)"
	@echo "  run              Run the dev server with hot reload"
	@echo "  test             Run all tests with coverage"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-e2e         Run e2e tests only"
	@echo "  lint             Run ruff linter"
	@echo "  format           Format code with ruff"
	@echo "  typecheck        Run mypy type checker"
	@echo "  migrate          Apply pending migrations"
	@echo "  migrate-create   Create a new migration (usage: make migrate-create msg='your message')"
	@echo "  docker-up        Start local dev stack"
	@echo "  docker-down      Stop local dev stack"

install:
	python -m pip install -r requirements.txt

dev:
	python -m pip install -r requirements.txt -r requirements-dev.txt

run:
	python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

test:
	python -m pytest --cov=src --cov-report=term-missing --cov-report=html -v

test-unit:
	python -m pytest -m unit -v

test-integration:
	python -m pytest -m integration -v

test-e2e:
	python -m pytest -m e2e -v

lint:
	python -m ruff check src tests

format:
	python -m ruff format src tests
	python -m ruff check --fix src tests

typecheck:
	python -m mypy src

migrate:
	python -m alembic upgrade head

migrate-create:
	python -m alembic revision --autogenerate -m "$(msg)"

docker-up:
	docker compose -f docker/docker-compose.yml up -d

docker-down:
	docker compose -f docker/docker-compose.yml down
