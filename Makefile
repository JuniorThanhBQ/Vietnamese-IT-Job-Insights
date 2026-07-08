SHELL := /bin/bash

.PHONY: help install dev-backend dev-frontend lint test compose-up compose-down fmt

help:
	@echo "Available targets: install, backend, frontend, lint, test, fmt, compose-up, compose-down"

install:
	@echo "Install dependencies for all services"
	@if [ -d backend ]; then \
		cd backend && python -m pip install --upgrade pip && python -m pip install -e . || true; \
	fi
	@if [ -d frontend ]; then \
		cd frontend && npm ci || true; \
	fi

backend:
	@echo "Run backend locally"
	@if [ -d backend ]; then \
		cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; \
	else \
		echo "backend not present"; \
	fi

frontend:
	@echo "Run frontend locally"
	@if [ -d frontend ]; then \
		cd frontend && npm run dev; \
	else \
		echo "frontend not present"; \
	fi

lint:
	@echo "Run lint for present services"
	@if [ -f scripts/run-pylint.sh ]; then \
		bash scripts/run-pylint.sh; \
	else \
		echo "No Python lint script found; skipping"; \
	fi
	@if [ -f scripts/run-eslint.sh ]; then \
		bash scripts/run-eslint.sh; \
	else \
		echo "No JavaScript lint script found; skipping"; \
	fi

test:
	@echo "Run tests for present services"
	@if [ -d backend/tests ]; then \
		cd backend && pytest -q; \
	else \
		echo "No backend tests found; skipping"; \
	fi
	@if [ -d frontend/tests ]; then \
		cd frontend && npm test; \
	else \
		echo "No frontend tests found; skipping"; \
	fi

fmt:
	@echo "Format code (best-effort)"
	@if [ -d backend ]; then \
		cd backend && black . || true; \
	fi
	@if [ -d frontend ]; then \
		cd frontend && npm run format || true; \
	fi

compose-up:
	@echo "Start local compose environment (docker-compose.local.yml)"
	@if [ -f docker-compose.local.yml ]; then \
		docker compose -f docker-compose.local.yml up -d --build; \
	else \
		echo "No docker-compose.local.yml found"; \
	fi

compose-down:
	@echo "Stop local compose environment"
	@if [ -f docker-compose.local.yml ]; then \
		docker compose -f docker-compose.local.yml down --remove-orphans; \
	else \
		echo "No docker-compose.local.yml found"; \
	fi

# Purpose:
#   Provides a unified CLI entry point for local development, CI workflows,
#   and monorepo orchestration. It abstracts service-specific commands (FastAPI,
#   Vite/React) and infrastructure ops (Docker Compose) into single-word targets.
#
# Design Philosophy:
#   - Idempotent & Defensive: Targets check for directory/file existence before 
#     execution to avoid failing abruptly in partial or dynamic environments.
#   - CI-Friendly: Utilizes non-blocking execution errors (`|| true`) for lint/test
#     stages where reporting takes precedence over hard pipeline failures.
#
# Usage:
#   make <target>  (e.g., 'make dev-backend', 'make compose-up', 'make test')
# ==============================================================================
