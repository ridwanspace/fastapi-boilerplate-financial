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
	pip install -r requirements.txt

dev:
	pip install -r requirements.txt -r requirements-dev.txt

run:
	uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

test:
	pytest --cov=src --cov-report=term-missing --cov-report=html -v

test-unit:
	pytest -m unit -v

test-integration:
	pytest -m integration -v

test-e2e:
	pytest -m e2e -v

lint:
	ruff check src tests

format:
	ruff format src tests
	ruff check --fix src tests

typecheck:
	mypy src

migrate:
	alembic upgrade head

migrate-create:
	alembic revision --autogenerate -m "$(msg)"

docker-up:
	docker compose -f docker/docker-compose.yml up -d

docker-down:
	docker compose -f docker/docker-compose.yml down
