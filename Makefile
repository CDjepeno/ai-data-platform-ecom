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

dbt-profile:
	nano ~/.dbt/profiles.yml
# ─────────────────────────────────────
#  SQLFluff
# ─────────────────────────────────────

SQL_INGESTION_DIR := src/etl_ecom/sql/bronze
SQL_DBT_DIR := src/etl_ecom/transformation

# 🔍 Lint SQL ingestion (Jinja simple)
lint-sql:
	@echo "🔍 Lint SQL ingestion..."
	poetry run sqlfluff lint $(SQL_INGESTION_DIR)

# 🔍 Lint dbt models
lint-dbt:
	@echo "🔍 Lint SQL dbt..."
	cd $(SQL_DBT_DIR) && poetry run sqlfluff lint models

# 🛠️ Fix SQL ingestion
fix-sql:
	@echo "🛠️ Auto-fix SQL ingestion..."
	poetry run sqlfluff fix $(SQL_INGESTION_DIR)

# 🛠️ Fix dbt models
fix-dbt:
	@echo "🛠️ Auto-fix SQL dbt..."
	cd $(SQL_DBT_DIR) && poetry run sqlfluff fix models

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
#  🪣 MinIO HELPERS
# ─────────────────────────────────────

MINIO_ALIAS ?= myminio
MINIO_BUCKET ?= ecom-etl

# 📦 Liste des buckets
minio-buckets:
	@echo "📦 Buckets disponibles:"
	mc ls $(MINIO_ALIAS)

# 📂 Contenu du bucket
minio-ls:
	@echo "📂 Contenu de $(MINIO_BUCKET):"
	mc ls $(MINIO_ALIAS)/$(MINIO_BUCKET)

# 🌲 Vue arborescente complète
minio-tree:
	@echo "🌲 Structure complète:"
	mc tree $(MINIO_ALIAS)/$(MINIO_BUCKET)

# 🔍 Recherche globale
minio-find:
	@echo "🔍 Recherche dans $(MINIO_BUCKET):"
	mc find $(MINIO_ALIAS)/$(MINIO_BUCKET)

# 📄 Lire un fichier
minio-cat:
ifndef FILE
	$(error ❌ Usage: make minio-cat FILE=path/to/file)
endif
	@echo "📄 Lecture $(FILE):"
	mc cat $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(FILE)

# ⬇️ Télécharger un fichier
minio-get:
ifndef FILE
	$(error ❌ Usage: make minio-get FILE=path/to/file)
endif
	mc cp $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(FILE) .

# ⬆️ Upload un fichier
minio-put:
ifndef FILE
	$(error ❌ Usage: make minio-put FILE=local_file DEST=path/in/bucket)
endif
ifndef DEST
	$(error ❌ Usage: make minio-put FILE=local_file DEST=path/in/bucket)
endif
	mc cp $(FILE) $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(DEST)

# 🔁 Sync dossier local → MinIO
minio-sync:
ifndef DIR
	$(error ❌ Usage: make minio-sync DIR=local_folder DEST=prefix)
endif
	mc mirror $(DIR) $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(DEST)

# 🧨 Supprimer fichier
minio-rm:
ifndef FILE
	$(error ❌ Usage: make minio-rm FILE=path/to/file)
endif
	mc rm $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(FILE)

# 🧹 Nettoyer un prefix (danger)
minio-clean-prefix:
ifndef PREFIX
	$(error ❌ Usage: make minio-clean-prefix PREFIX=raw/)
endif
	mc rm --recursive --force $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(PREFIX)

# 📊 Taille du bucket
minio-du:
	mc du $(MINIO_ALIAS)/$(MINIO_BUCKET)

# 🧠 Voir metadata d’un fichier
minio-stat:
ifndef FILE
	$(error ❌ Usage: make minio-stat FILE=path/to/file)
endif
	mc stat $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(FILE)

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

show-all-tables:
	$(PYTHON) $(DB_INSPECT) "$(DBT_DUCKDB_PATH_DEV)" query "SHOW ALL TABLES"

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
#  🧊 ICEBERG HELPERS
# ─────────────────────────────────────

iceberg-list-tables:
	$(PYTHON) -m scripts.iceberg.list_tables

iceberg-schema:
ifndef TABLE
	$(error ❌ Usage: make iceberg-schema TABLE=bronze.users)
endif
	$(PYTHON) -m scripts.iceberg.schema $(TABLE)

iceberg-count:
ifndef TABLE
	$(error ❌ Usage: make iceberg-count TABLE=bronze.users)
endif
	$(PYTHON) -m scripts.iceberg.count $(TABLE)

iceberg-history:
ifndef TABLE
	$(error ❌ Usage: make iceberg-history TABLE=bronze.users)
endif
	$(PYTHON) -m scripts.iceberg.history $(TABLE)

iceberg-current-snapshot:
ifndef TABLE
	$(error ❌ Usage: make iceberg-current-snapshot TABLE=bronze.users)
endif
	$(PYTHON) -m scripts.iceberg.current_snapshot $(TABLE)

iceberg-drop-table:
ifndef TABLE
	$(error ❌ Usage: make iceberg-drop-table TABLE=bronze.users)
endif
	$(PYTHON) -m scripts.iceberg.drop_table $(TABLE)

iceberg-drop-all:
	$(PYTHON) -m scripts.iceberg.drop_all_tables

iceberg-preview:
ifndef TABLE
	$(error ❌ Usage: make iceberg-preview TABLE=bronze.users)
endif
	$(PYTHON) -m scripts.iceberg.preview $(TABLE)

iceberg-describe:
ifndef TABLE
	$(error ❌ Usage: make iceberg-describe TABLE=bronze.users)
endif
	$(PYTHON) -m scripts.iceberg.describe $(TABLE)

iceberg-snapshots:
ifndef TABLE
	$(error ❌ Usage: make iceberg-snapshots TABLE=bronze.users)
endif
	$(PYTHON) -m scripts.iceberg.snapshots $(TABLE)

# ─────────────────────────────────────
#  🔎 TRINO HELPERS
# ─────────────────────────────────────

TRINO_CONTAINER := trino

# Ouvre le shell Trino
trino:
	docker exec -it $(TRINO_CONTAINER) trino

# Execute une query
trino-query:
ifndef SQL
	$(error ❌ Usage: make trino-query SQL="SHOW SCHEMAS FROM iceberg")
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "$(SQL)"

# Liste catalogs
trino-catalogs:
	docker exec -i $(TRINO_CONTAINER) trino --execute "SHOW CATALOGS"

# Liste schemas iceberg
trino-schemas:
	docker exec -i $(TRINO_CONTAINER) trino --execute "SHOW SCHEMAS FROM iceberg"

# Liste tables d'un schema
trino-tables:
ifndef SCHEMA
	$(error ❌ Usage: make trino-tables SCHEMA=raw)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "SHOW TABLES FROM iceberg.$(SCHEMA)"

# Preview table
trino-preview:
ifndef TABLE
	$(error ❌ Usage: make trino-preview TABLE=raw.users)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "SELECT * FROM iceberg.$(TABLE) LIMIT 10"

# Count table
trino-count:
ifndef TABLE
	$(error ❌ Usage: make trino-count TABLE=raw.users)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "SELECT COUNT(*) FROM iceberg.$(TABLE)"

# Describe table
trino-describe:
ifndef TABLE
	$(error ❌ Usage: make trino-describe TABLE=raw.users)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "DESCRIBE iceberg.$(TABLE)"

# Drop table
trino-drop-table:
ifndef TABLE
	$(error ❌ Usage: make trino-drop-table TABLE=raw.users)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "DROP TABLE iceberg.$(TABLE)"

# Drop schema complet
trino-drop-schema:
ifndef SCHEMA
	$(error ❌ Usage: make trino-drop-schema SCHEMA=raw)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "DROP SCHEMA iceberg.$(SCHEMA) CASCADE"

# Voir create table
trino-show-create:
ifndef TABLE
	$(error ❌ Usage: make trino-show-create TABLE=raw.users)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "SHOW CREATE TABLE iceberg.$(TABLE)"


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
	@echo "  make fix-dbt               → Auto-fix SQL dbt"
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
	@echo "  make dbt-profile           → Edit dbt profile"
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
	@echo "  make show-all-tables       → Vue globale tables"
	@echo ""
	@echo "🧨 MAINTENANCE"
	@echo "  make reset-db              → Reset DuckDB"
	@echo "  make reset-db-safe         → Reset avec confirmation"
	@echo ""
	@echo "🪣 MINIO"
	@echo "  make minio-buckets         → Liste buckets"
	@echo "  make minio-ls              → Contenu bucket"
	@echo "  make minio-tree            → Vue complète"
	@echo "  make minio-find            → Recherche fichiers"
	@echo "  make minio-cat FILE=...    → Lire fichier"
	@echo "  make minio-put FILE=... DEST=..."
	@echo "  make minio-sync DIR=... DEST=..."
	@echo "  make minio-clean-prefix PREFIX=..."
	@echo ""
	@echo "🧊 ICEBERG"
	@echo "  make iceberg-list-tables                 → Liste les tables Iceberg"
	@echo "  make iceberg-schema TABLE=bronze.users  → Affiche le schéma"
	@echo "  make iceberg-preview TABLE=bronze.users  → Aperçu des données"
	@echo "  make iceberg-count TABLE=bronze.users  → Compte les lignes"
	@echo "  make iceberg-history TABLE=bronze.users → Historique des snapshots"
	@echo "  make iceberg-current-snapshot TABLE=bronze.users → Snapshot actif"
	@echo "  make iceberg-drop-table TABLE=bronze.users      → suppression de la table"
	@echo "  make iceberg-describe TABLE=bronze.users      → description de la table"
	@echo "  make iceberg-drop-all      → suppression de toutes les tables"
	@echo "  make iceberg-snapshots TABLE=bronze.users      → affiche les snapshots de la table"
	@echo ""
	@echo "🔦 TRINO"
	@echo "  make trino                               → Ouvrir shell Trino"
	@echo "  make trino-catalogs                      → Liste les catalogs"
	@echo "  make trino-schemas                       → Liste les schemas Iceberg"
	@echo "  make trino-tables SCHEMA=raw             → Liste les tables d’un schema"
	@echo "  make trino-preview TABLE=raw.users       → Aperçu d’une table"
	@echo "  make trino-count TABLE=raw.users         → Nombre de lignes"
	@echo "  make trino-describe TABLE=raw.users      → Description d’une table"
	@echo "  make trino-show-create TABLE=raw.users   → Affiche le CREATE TABLE"
	@echo "  make trino-drop-table TABLE=raw.users    → Supprime une table"
	@echo "  make trino-drop-schema SCHEMA=raw        → Supprime un schema"
	@echo "  make trino-query SQL='SELECT * FROM iceberg.raw.users LIMIT 10'"
	@echo ""
	@echo "══════════════════════════════════════════"
	@echo ""