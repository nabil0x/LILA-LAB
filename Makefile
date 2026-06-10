# ─────────────────────────────────────────────────────────
# LILA Lab — Makefile
# Common tasks for pipeline development and maintenance.
#
# Quick reference:
#   make install       Install all dependencies
#   make lint          Lint Python code with Ruff
#   make format        Format Python code with Ruff
#   make test          Run pytest (if tests/ exists)
#   make docker        Build pipeline Docker image
#   make clean         Remove build artifacts and caches
#   make help          Show this help
# ─────────────────────────────────────────────────────────

SHELL := /bin/bash
PYTHON := python3

.PHONY: install install-core install-llm install-dev install-all
.PHONY: lint format test docker clean help

# ── Install ────────────────────────────────────────────

install:
	$(PYTHON) -m pip install -e ".[all]"

install-core:
	$(PYTHON) -m pip install -e ".[core]"

install-llm:
	$(PYTHON) -m pip install -e ".[core,llm]"

install-dev:
	$(PYTHON) -m pip install -e ".[dev]"

install-all:
	$(PYTHON) -m pip install -e ".[all]"

# ── Lint & Format ─────────────────────────────────────

lint:
	ruff check pipelines/shared/ pipelines/template/ infrastructure/
	ruff check --no-cache pipelines/beni/ --select E,W,F,I --ignore E501,E741 || \
		echo "Note: beni/ linting is advisory (run separately)"

format:
	ruff format pipelines/shared/ pipelines/template/ infrastructure/ --check
	ruff format pipelines/beni/ --check || \
		echo "Note: beni/ formatting check is advisory (run separately)"

format-fix:
	ruff format pipelines/shared/ pipelines/template/ infrastructure/
	ruff format pipelines/beni/ 2>/dev/null || true

lint-fix:
	ruff check --fix pipelines/shared/ pipelines/template/ infrastructure/

# ── Tests ──────────────────────────────────────────────

test:
	$(PYTHON) -m pytest $(ARGS)

test-cov:
	$(PYTHON) -m pytest --cov=pipelines --cov-report=term-missing $(ARGS)

# ── Docker ────────────────────────────────────────────

docker:
	docker build -t lila-lab:latest .

docker-compose-up:
	docker compose up

docker-compose-build:
	docker compose build

# ── Cleanup ───────────────────────────────────────────

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache .dmypy.json 2>/dev/null || true

# ── Help ──────────────────────────────────────────────

help:
	@echo "LILA Lab — Makefile"
	@echo ""
	@echo "install           Install all dependencies (pip install -e .[all])"
	@echo "install-core      Install only core deps (pandas, sklearn, etc.)"
	@echo "install-llm       Install core + LLM annotation deps"
	@echo "install-dev       Install dev deps (ruff, pytest)"
	@echo "lint              Lint all pipeline code with Ruff"
	@echo "format            Check formatting (dry-run)"
	@echo "format-fix        Apply formatting fixes"
	@echo "lint-fix          Apply lint fixes"
	@echo "test              Run pytest"
	@echo "test-cov          Run pytest with coverage"
	@echo "docker            Build pipeline Docker image"
	@echo "docker-compose-up Start all services via docker compose"
	@echo "clean             Remove build artifacts"
	@echo ""
	@echo "See pyproject.toml for Ruff and pytest configuration."
