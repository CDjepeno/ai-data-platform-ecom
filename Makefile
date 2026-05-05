# ─────────────────────────────────────
#  Variables
# ─────────────────────────────────────
include docker/.env
export

DBT_DIR := src/etl_ecom/transformation
DBT := poetry run dbt
PYTHON := poetry run python
DB_INSPECT := scripts/db_inspect.py

# 🔥 NEW
SEED_DAILY := scripts/seed/seed_daily_growth.sql

# ─────────────────────────────────────
#  Commandes dbt
# ─────────────────────────────────────

.PHONY: dbt-init dbt-run dbt-test dbt-build dbt-docs dbt-debug dbt-seed

dbt-init:
	@echo "Initialisation de dbt dans $(DBT_DIR)..."
	cd $(DBT_DIR) && $(DBT) init

dbt-run:
	@echo "Exécution des modèles dbt..."
	cd $(DBT_DIR) && $(DBT) run

dbt-test:
	@echo "Lancement des tests dbt..."
	cd $(DBT_DIR) && $(DBT) test

dbt-build:
	@echo "Build complet (run + test)..."
	cd $(DBT_DIR) && $(DBT) build

dbt-docs:
	@echo "Génération et ouverture de la documentation..."
	cd $(DBT_DIR) && $(DBT) docs generate
	cd $(DBT_DIR) && $(DBT) docs serve

dbt-debug:
	@echo "Vérification de la configuration dbt..."
	cd $(DBT_DIR) && $(DBT) debug

dbt-seed:
	@echo "Chargement des seeds..."
	cd $(DBT_DIR) && $(DBT) seed

# ─────────────────────────────────────
#  SQLFluff
# ─────────────────────────────────────

lint-sql:
	@echo "Lint SQL (global)..."
	poetry run sqlfluff lint .

lint-dbt:
	@echo "Lint SQL dbt..."
	cd $(DBT_DIR) && poetry run sqlfluff lint . --templater dbt

fix-sql:
	@echo "Auto-fix SQL..."
	poetry run sqlfluff fix .

# ─────────────────────────────────────
#  Simulation DATA 🔥
# ─────────────────────────────────────

seed-daily:
	@echo "🌱 Simulation quotidienne..."
	psql "postgresql://postgres:Dulonx95*@localhost:5434/ecom_db" -f $(SEED_DAILY)

# 🔥 Simulation N jours
simulate-days:
ifndef DAYS
	$(error ❌ Usage: make simulate-days DAYS=10)
endif
	@echo "📆 Simulation de $(DAYS) jours..."
	for i in $$(seq 1 $(DAYS)); do \
		echo "➡️  Jour $$i"; \
		psql $(DB_URL) -f $(SEED_DAILY); \
		make run; \
	done

# ─────────────────────────────────────
#  Inspection DuckDB
# ─────────────────────────────────────

schemas:
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" schemas

check-tables:
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" tables

tables-schema:
ifndef SCHEMA
	$(error ❌ Usage: make tables-schema SCHEMA=metadata)
endif
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" tables_schema "$(SCHEMA)"

describe-table:
ifndef TABLE
	$(error ❌ Usage: make describe-table TABLE=metadata.etl_watermark)
endif
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" describe "$(TABLE)"

count-rows:
ifndef TABLE
	$(error ❌ Usage: make count-rows TABLE=metadata.etl_watermark)
endif
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" count "$(TABLE)"

query:
ifndef SQL
	$(error ❌ Usage: make query SQL="SELECT * FROM metadata.etl_watermark")
endif
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" query "$(SQL)"

preview:
ifndef TABLE
	$(error ❌ Usage: make preview TABLE=metadata.etl_watermark)
endif
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" query "SELECT * FROM $(TABLE) ORDER BY 1 DESC LIMIT 10"

last-watermark:
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" query "SELECT * FROM metadata.etl_watermark ORDER BY high_watermark DESC LIMIT 10"

last-metrics:
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" query "SELECT * FROM metadata.etl_metrics ORDER BY processed_at DESC LIMIT 10"


count-all:
ifndef TABLE
	$(error ❌ Usage: make count-all TABLE=metadata.etl_watermark)
endif
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" query "SELECT COUNT(*) AS total FROM $(TABLE)"

db-tree:
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" tree

reset-db:
	@echo "🧨 Reset de la base DuckDB..."
	rm -f $(DBT_DUCKDB_PATH_DEV)
	@echo "✅ Base supprimée"

reset-db-safe:
	@read -p "⚠️  Supprimer la DB ? (y/n): " confirm && [ "$$confirm" = "y" ] || exit 1
	rm -f $(DBT_DUCKDB_PATH_DEV)
	@echo "✅ Base supprimée"

# ─────────────────────────────────────
#  Pipeline
# ─────────────────────────────────────

run:
	@echo "🚀 Lancement de l'application ETL..."
	poetry run python -m src.etl_ecom.pipeline

# 🔥 FULL DAILY FLOW
daily-run: seed-daily run

# 🔥 FULL DATA STACK
full-run: seed-daily run dbt-build

# ─────────────────────────────────────
#  Commandes générales
# ─────────────────────────────────────

install:
	@echo "Installation des dépendances Poetry..."
	poetry install

lint:
	@echo "Linting Python avec ruff..."
	poetry run ruff check src/

test:
	@echo "Lancement des tests..."
	poetry run pytest

# ─────────────────────────────────────
#  Aide
# ─────────────────────────────────────

help:
	@echo ""
	@echo "══════════════════════════════════════════"
	@echo "        📊 ECOM DATA PLATFORM"
	@echo "══════════════════════════════════════════"
	@echo ""
	@echo "📦 INSTALLATION"
	@echo "  make install               → Installer les dépendances"
	@echo ""
	@echo "🧪 QUALITÉ CODE"
	@echo "  make lint                  → Lint Python (ruff)"
	@echo "  make lint-sql              → Lint SQL global"
	@echo "  make lint-dbt              → Lint SQL dbt"
	@echo "  make fix-sql               → Auto-fix SQL"
	@echo ""
	@echo "🌱 DATA SIMULATION"
	@echo "  make seed-daily            → Générer data (1 jour)"
	@echo "  make simulate-days DAYS=10 → Simuler plusieurs jours"
	@echo ""
	@echo "🚀 PIPELINE"
	@echo "  make run                   → Lancer ETL"
	@echo "  make daily-run             → seed + ETL"
	@echo "  make full-run              → seed + ETL + dbt"
	@echo ""
	@echo "🧱 DBT"
	@echo "  make dbt-run               → Run modèles"
	@echo "  make dbt-test              → Tests"
	@echo "  make dbt-build             → Run + test"
	@echo "  make dbt-docs              → Docs"
	@echo "  make dbt-debug             → Debug config"
	@echo "  make dbt-seed              → Seed dbt"
	@echo ""
	@echo "🗄️ DUCKDB INSPECTION"
	@echo "  make schemas               → Liste schemas"
	@echo "  make check-tables          → Liste tables"
	@echo "  make tables-schema SCHEMA=metadata"
	@echo "  make describe-table TABLE=metadata.etl_watermark"
	@echo "  make count-rows TABLE=metadata.etl_watermark"
	@echo "  make preview TABLE=metadata.etl_watermark"
	@echo "  make last TABLE=metadata.etl_watermark"
	@echo "  make count-all TABLE=metadata.etl_watermark"
	@echo "  make query SQL='SELECT * FROM table'"
	@echo "  make db-tree               → Vue globale DB"
	@echo ""
	@echo "🧨 MAINTENANCE"
	@echo "  make reset-db              → Reset DuckDB"
	@echo "  make reset-db-safe         → Reset avec confirmation"
	@echo ""
	@echo "══════════════════════════════════════════"
	@echo ""