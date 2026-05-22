# ─────────────────────────────────────
#  Variables
# ─────────────────────────────────────

POETRY  := poetry
PYTEST  := $(POETRY) run pytest
RUFF    := $(POETRY) run ruff
PYTHON  := $(POETRY) run python

COV_MODULES := --cov=domain --cov=application --cov=infrastructure

# ─────────────────────────────────────
#  Installation
# ─────────────────────────────────────

.PHONY: install

install:
	@echo "📦 Installing dependencies..."
	$(POETRY) install

# ─────────────────────────────────────
#  Run
# ─────────────────────────────────────

.PHONY: run-mcp run-slack run-inspector

run-mcp:
	@echo "🤖 Starting MCP server..."
	$(PYTHON) -m infrastructure.mcp.server

run-slack:
	@echo "💬 Starting Slack bot..."
	$(PYTHON) -m infrastructure.adapters.slack.bot

run-inspector:
	@echo "🔍 Starting MCP Inspector (no auth)..."
	DANGEROUSLY_OMIT_AUTH=true mcp-inspector

# ─────────────────────────────────────
#  Tests
# ─────────────────────────────────────

.PHONY: test test-unit test-int test-domain test-application

test:
	@echo "🧪 Running all tests..."
	$(PYTEST) -v

test-unit:
	@echo "🧪 Running unit tests (domain + application)..."
	$(PYTEST) tests/unit/ -v

test-int:
	@echo "🧪 Running integration tests (adapters)..."
	$(PYTEST) tests/integration/ -v

test-domain:
	@echo "🧪 Running domain tests only..."
	$(PYTEST) tests/unit/domain/ -v

test-application:
	@echo "🧪 Running application tests only..."
	$(PYTEST) tests/unit/application/ -v

# ─────────────────────────────────────
#  Coverage
# ─────────────────────────────────────

.PHONY: coverage coverage-html

coverage:
	@echo "📊 Running tests with coverage..."
	$(PYTEST) $(COV_MODULES) --cov-report=term-missing -v

coverage-html:
	@echo "📊 Generating HTML coverage report..."
	$(PYTEST) $(COV_MODULES) --cov-report=html -v
	@echo "✅ Report generated → htmlcov/index.html"

# ─────────────────────────────────────
#  Code quality
# ─────────────────────────────────────

.PHONY: lint format format-check check

lint:
	@echo "🔍 Linting with ruff..."
	$(RUFF) check .

format:
	@echo "🛠️ Formatting with ruff..."
	$(RUFF) format .

format-check:
	@echo "🔍 Checking format with ruff..."
	$(RUFF) format --check .

check: lint format-check coverage
	@echo "✅ All checks passed"

# ─────────────────────────────────────
#  Cleanup
# ─────────────────────────────────────

.PHONY: clean

clean:
	@echo "🧨 Cleaning cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -delete 2>/dev/null || true
	@echo "✅ Cleaned"

# ─────────────────────────────────────
#  Help
# ─────────────────────────────────────

.PHONY: help
.DEFAULT_GOAL := help

help:
	@echo ""
	@echo "══════════════════════════════════════════"
	@echo "        🤖 MCP GATEWAY"
	@echo "══════════════════════════════════════════"
	@echo ""
	@echo "📦 INSTALLATION"
	@echo "  make install                → Install Poetry dependencies"
	@echo ""
	@echo "🚀 RUN"
	@echo "  make run-mcp                → Start MCP server (stdio)"
	@echo "  make run-slack              → Start Slack bot (Socket Mode)"
	@echo "  make run-inspector          → Start MCP Inspector (Postman for MCP)"
	@echo ""
	@echo "🧪 TESTS"
	@echo "  make test                   → Run all tests"
	@echo "  make test-unit              → Run unit tests only (domain + application)"
	@echo "  make test-int               → Run integration tests only (adapters)"
	@echo "  make test-domain            → Run domain tests only"
	@echo "  make test-application       → Run application tests only"
	@echo ""
	@echo "📊 COVERAGE"
	@echo "  make coverage               → Tests + coverage report in terminal"
	@echo "  make coverage-html          → Tests + HTML report (htmlcov/index.html)"
	@echo ""
	@echo "🔍 CODE QUALITY"
	@echo "  make lint                   → Lint with ruff"
	@echo "  make format                 → Auto-format with ruff"
	@echo "  make format-check           → Check format without modifying"
	@echo "  make check                  → lint + format-check + coverage (CI)"
	@echo ""
	@echo "🧨 MAINTENANCE"
	@echo "  make clean                  → Remove cache and coverage files"
	@echo "══════════════════════════════════════════"
	@echo ""