.PHONY: up down dev logs migrate seed test lint

# Production
up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f bot

# Development
dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

# Database
migrate:
	docker compose exec bot alembic upgrade head

migrate-create:
	docker compose exec bot alembic revision --autogenerate -m "$(msg)"

seed:
	docker compose exec bot python -m scripts.seed_categories
	docker compose exec bot python -m scripts.seed_currencies

# Testing
test:
	pytest tests/ -v --cov=app

# Linting
lint:
	ruff check app/ tests/
	ruff format --check app/ tests/

format:
	ruff check --fix app/ tests/
	ruff format app/ tests/
