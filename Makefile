# ───────────────────────────────────── #  Variables # ───────────────────────────────────── m
ETL_DIR := src/etl_ecom
MCP_DIR := src/mcp
ENV_FILE := docker/.env.local

DBT_DIR := $(ETL_DIR)/etl_ecom/transformation

POETRY := poetry -C $(ETL_DIR)

PYTHON := $(POETRY) run python
DBT := $(POETRY) run dbt

SEED_DAILY := $(ETL_DIR)/etl_ecom/scripts/seed/seed_daily_growth.sql

DB_INSPECT_MODULE := etl_ecom.scripts.db_inspect

SQL_INGESTION_DIR := $(ETL_DIR)/etl_ecom/sql/bronze
SQL_DBT_DIR := $(ETL_DIR)/etl_ecom/transformation

TRINO_CONTAINER := trino

MINIO_ALIAS ?= myminio
MINIO_BUCKET ?= ecom-etl

# ─────────────────────────────────────
#  dbt commands
# ─────────────────────────────────────

.PHONY: dbt-init dbt-run dbt-test dbt-build dbt-docs dbt-debug dbt-seed dbt-parse test-etl test-mcp test

dbt-init:
	@echo "Initializing dbt in $(DBT_DIR)..."
	cd $(DBT_DIR) && $(DBT) init

dbt-parse:
	@echo "Parsing dbt project..."
	cd $(DBT_DIR) && $(DBT) parse

dbt-run:
	@echo "Running dbt models..."
	cd $(DBT_DIR) && $(DBT) run

dbt-test:
	@echo "Running dbt tests..."
	cd $(DBT_DIR) && $(DBT) test

dbt-build:
	@echo "Full build (run + test)..."
	cd $(DBT_DIR) && $(DBT) build

dbt-docs:
	@echo "Generating and opening documentation..."
	cd $(DBT_DIR) && $(DBT) docs generate
	cd $(DBT_DIR) && $(DBT) docs serve

dbt-debug:
	@echo "Verifying dbt configuration..."
	cd $(DBT_DIR) && $(DBT) debug

dbt-seed:
	@echo "Loading dbt seeds..."
	cd $(DBT_DIR) && $(DBT) seed

dbt-profile:
	nano ~/.dbt/profiles.yml

# ─────────────────────────────────────
#  SQLFluff
# ─────────────────────────────────────

lint-sql:
	@echo "🔍 Lint SQL ingestion..."
	$(POETRY) run sqlfluff lint $(SQL_INGESTION_DIR)

lint-dbt:
	@echo "🔍 Lint dbt SQL..."
	cd $(SQL_DBT_DIR) && $(POETRY) run sqlfluff lint models

fix-sql:
	@echo "🛠️ Auto-fix SQL ingestion..."
	$(POETRY) run sqlfluff fix $(SQL_INGESTION_DIR)

fix-dbt:
	@echo "🛠️ Auto-fix dbt SQL..."
	cd $(SQL_DBT_DIR) && $(POETRY) run sqlfluff fix models

# ─────────────────────────────────────
#  DATA simulation
# ─────────────────────────────────────

seed-daily:
	@echo "🌱 Daily simulation..."
	psql "postgresql://postgres:Dulonx95*@localhost:5434/ecom_db" -f $(SEED_DAILY)

simulate-days:
ifndef DAYS
	$(error ❌ Usage: make simulate-days DAYS=10)
endif
	@echo "📆 Simulating $(DAYS) days..."
	for i in $$(seq 1 $(DAYS)); do \
		echo "➡️ Day $$i"; \
		psql $(DB_URL) -f $(SEED_DAILY); \
		make run; \
	done

# ─────────────────────────────────────
#  MinIO HELPERS
# ─────────────────────────────────────

minio-buckets:
	@echo "📦 Available buckets:"
	mc ls $(MINIO_ALIAS)

minio-ls:
	@echo "📂 Contents of $(MINIO_BUCKET):"
	mc ls $(MINIO_ALIAS)/$(MINIO_BUCKET)

minio-tree:
	@echo "🌲 Full structure:"
	mc tree $(MINIO_ALIAS)/$(MINIO_BUCKET)

minio-find:
	@echo "🔍 Searching $(MINIO_BUCKET):"
	mc find $(MINIO_ALIAS)/$(MINIO_BUCKET)

minio-cat:
ifndef FILE
	$(error ❌ Usage: make minio-cat FILE=path/to/file)
endif
	@echo "📄 Reading $(FILE):"
	mc cat $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(FILE)

minio-get:
ifndef FILE
	$(error ❌ Usage: make minio-get FILE=path/to/file)
endif
	mc cp $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(FILE) .

minio-put:
ifndef FILE
	$(error ❌ Usage: make minio-put FILE=local_file DEST=path/in/bucket)
endif
ifndef DEST
	$(error ❌ Usage: make minio-put FILE=local_file DEST=path/in/bucket)
endif
	mc cp $(FILE) $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(DEST)

minio-sync:
ifndef DIR
	$(error ❌ Usage: make minio-sync DIR=local_folder DEST=prefix)
endif
	mc mirror $(DIR) $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(DEST)

minio-rm:
ifndef FILE
	$(error ❌ Usage: make minio-rm FILE=path/to/file)
endif
	mc rm $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(FILE)

minio-clean-prefix:
ifndef PREFIX
	$(error ❌ Usage: make minio-clean-prefix PREFIX=raw/)
endif
	mc rm --recursive --force $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(PREFIX)

minio-du:
	mc du $(MINIO_ALIAS)/$(MINIO_BUCKET)

minio-stat:
ifndef FILE
	$(error ❌ Usage: make minio-stat FILE=path/to/file)
endif
	mc stat $(MINIO_ALIAS)/$(MINIO_BUCKET)/$(FILE)

# ─────────────────────────────────────
#  Inspection DuckDB
# ─────────────────────────────────────

schemas:
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" schemas

check-tables:
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" tables

tables-schema:
ifndef SCHEMA
	$(error ❌ Usage: make tables-schema SCHEMA=metadata)
endif
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" tables_schema "$(SCHEMA)"

describe-table:
ifndef TABLE
	$(error ❌ Usage: make describe-table TABLE=metadata.etl_watermark)
endif
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" describe "$(TABLE)"

count-rows:
ifndef TABLE
	$(error ❌ Usage: make count-rows TABLE=metadata.etl_watermark)
endif
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" count "$(TABLE)"

show-all-tables:
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" query "SHOW ALL TABLES"

query:
ifndef SQL
	$(error ❌ Usage: make query SQL='SELECT * FROM metadata.etl_watermark')
endif
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" query "$(SQL)"

preview:
ifndef TABLE
	$(error ❌ Usage: make preview TABLE=metadata.etl_watermark)
endif
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" query "SELECT * FROM $(TABLE) ORDER BY 1 DESC LIMIT 10"

last-watermark:
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" query "SELECT * FROM metadata.etl_watermark ORDER BY high_watermark DESC LIMIT 10"

last-metrics:
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" query "SELECT * FROM metadata.etl_metrics ORDER BY processed_at DESC LIMIT 10"

count-all:
ifndef TABLE
	$(error ❌ Usage: make count-all TABLE=metadata.etl_watermark)
endif
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" query "SELECT COUNT(*) AS total FROM $(TABLE)"

db-tree:
	$(PYTHON) -m $(DB_INSPECT_MODULE) "$(DBT_DUCKDB_PATH_DEV)" tree

reset-db:
	@echo "🧨 Resetting DuckDB database..."
	rm -f $(DBT_DUCKDB_PATH_DEV)
	@echo "✅ Database removed"

reset-db-safe:
	@read -p "⚠️ Delete the database? (y/n): " confirm && [ "$$confirm" = "y" ] || exit 1
	rm -f $(DBT_DUCKDB_PATH_DEV)
	@echo "✅ Database removed"

# ─────────────────────────────────────
#  Pipeline
# ─────────────────────────────────────

run:
	@echo "🚀 Launching ETL pipeline..."
	poetry -C $(ETL_DIR) run python -m etl_ecom.pipeline

daily-run: seed-daily run

full-run: seed-daily run dbt-build

# ─────────────────────────────────────
#  ICEBERG HELPERS
# ─────────────────────────────────────

iceberg-list-tables:
	$(PYTHON) -m etl_ecom.scripts.iceberg.list_tables

iceberg-schema:
ifndef TABLE
	$(error ❌ Usage: make iceberg-schema TABLE=bronze.users)
endif
	$(PYTHON) -m etl_ecom.scripts.iceberg.schema $(TABLE)

iceberg-count:
ifndef TABLE
	$(error ❌ Usage: make iceberg-count TABLE=bronze.users)
endif
	$(PYTHON) -m etl_ecom.scripts.iceberg.count $(TABLE)

iceberg-history:
ifndef TABLE
	$(error ❌ Usage: make iceberg-history TABLE=bronze.users)
endif
	$(PYTHON) -m etl_ecom.scripts.iceberg.history $(TABLE)

iceberg-current-snapshot:
ifndef TABLE
	$(error ❌ Usage: make iceberg-current-snapshot TABLE=bronze.users)
endif
	$(PYTHON) -m etl_ecom.scripts.iceberg.current_snapshot $(TABLE)

iceberg-drop-table:
ifndef TABLE
	$(error ❌ Usage: make iceberg-drop-table TABLE=bronze.users)
endif
	$(PYTHON) -m etl_ecom.scripts.iceberg.drop_table $(TABLE)

iceberg-drop-all:
	$(PYTHON) -m etl_ecom.scripts.iceberg.drop_all_tables

iceberg-drop-dbt:
	$(PYTHON) -m etl_ecom.scripts.iceberg.drop_dbt_tables

iceberg-preview:
ifndef TABLE
	$(error ❌ Usage: make iceberg-preview TABLE=bronze.users)
endif
	$(PYTHON) -m etl_ecom.scripts.iceberg.preview $(TABLE)

iceberg-describe:
ifndef TABLE
	$(error ❌ Usage: make iceberg-describe TABLE=bronze.users)
endif
	$(PYTHON) -m etl_ecom.scripts.iceberg.describe $(TABLE)

iceberg-snapshots:
ifndef TABLE
	$(error ❌ Usage: make iceberg-snapshots TABLE=bronze.users)
endif
	$(PYTHON) -m etl_ecom.scripts.iceberg.snapshots $(TABLE)

# ─────────────────────────────────────
#  TRINO HELPERS
# ─────────────────────────────────────

trino:
	docker exec -it $(TRINO_CONTAINER) trino

trino-query:
ifndef SQL
	$(error ❌ Usage: make trino-query SQL="SHOW SCHEMAS FROM iceberg")
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "$(SQL)"

trino-catalogs:
	docker exec -i $(TRINO_CONTAINER) trino --execute "SHOW CATALOGS"

trino-schemas:
	docker exec -i $(TRINO_CONTAINER) trino --execute "SHOW SCHEMAS FROM iceberg"

trino-tables:
ifndef SCHEMA
	$(error ❌ Usage: make trino-tables SCHEMA=raw)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "SHOW TABLES FROM iceberg.$(SCHEMA)"

trino-preview:
ifndef TABLE
	$(error ❌ Usage: make trino-preview TABLE=raw.users)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "SELECT * FROM iceberg.$(TABLE) LIMIT 10"

trino-count:
ifndef TABLE
	$(error ❌ Usage: make trino-count TABLE=raw.users)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "SELECT COUNT(*) FROM iceberg.$(TABLE)"

trino-describe:
ifndef TABLE
	$(error ❌ Usage: make trino-describe TABLE=raw.users)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "DESCRIBE iceberg.$(TABLE)"

trino-drop-table:
ifndef TABLE
	$(error ❌ Usage: make trino-drop-table TABLE=raw.users)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "DROP TABLE iceberg.$(TABLE)"

trino-drop-schema:
ifndef SCHEMA
	$(error ❌ Usage: make trino-drop-schema SCHEMA=raw)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "DROP SCHEMA iceberg.$(SCHEMA) CASCADE"

trino-show-create:
ifndef TABLE
	$(error ❌ Usage: make trino-show-create TABLE=raw.users)
endif
	docker exec -i $(TRINO_CONTAINER) trino --execute "SHOW CREATE TABLE iceberg.$(TABLE)"

# ─────────────────────────────────────
#  fastAPI
# ─────────────────────────────────────

run-api:
	poetry run uvicorn src.fast_api.main:app --reload

# ─────────────────────────────────────
#  General commands
# ─────────────────────────────────────

install:
	@echo "Installing Poetry dependencies..."
	$(POETRY) install

lint:
	@echo "Linting Python with ruff..."
	$(POETRY) run ruff check $(ETL_DIR)

test-etl:
	@echo "🧪 Running etl_ecom tests..."
	cd $(ETL_DIR) && poetry run python -m pytest tests/ -v --tb=short

test-mcp:
	@echo "🧪 Running mcp tests..."
	cd $(MCP_DIR) && poetry run python -m pytest tests/unit/ -v --tb=short

test:
	@echo "🧪 Running all unit tests..."
	@$(MAKE) test-etl
	@$(MAKE) test-mcp
	@echo "✅ All tests passed"

# ─────────────────────────────────────
#  Observability (OTel + Tempo)
# ─────────────────────────────────────

K8S_NAMESPACE     := ecom-local
MONITORING_NAMESPACE := monitoring
HELM_VALUES_DIR   := infrastructure/kubernetes/overlays/local/helm-values

.PHONY: otel-repos otel-install otel-uninstall monitoring-upgrade

otel-repos:
	helm repo add grafana https://grafana.github.io/helm-charts
	helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
	helm repo update

otel-install: otel-repos
	@echo "🔭 Installing Tempo..."
	helm upgrade --install tempo grafana/tempo \
		-n $(K8S_NAMESPACE) \
		-f $(HELM_VALUES_DIR)/tempo-values.yml
	@echo "📡 Installing OTel Collector..."
	helm upgrade --install otel-collector open-telemetry/opentelemetry-collector \
		-n $(K8S_NAMESPACE) \
		-f $(HELM_VALUES_DIR)/otel-collector-values.yml

otel-uninstall:
	helm uninstall tempo -n $(K8S_NAMESPACE) || true
	helm uninstall otel-collector -n $(K8S_NAMESPACE) || true

monitoring-upgrade:
	@echo "📊 Installing/upgrading kube-prometheus-stack..."
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update
	helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
		-n $(MONITORING_NAMESPACE) --create-namespace \
		-f infrastructure/kubernetes/overlays/local/prometheus-values.yml

# ─────────────────────────────────────
#  Airflow
# ─────────────────────────────────────

AIRFLOW_NAMESPACE := airflow

airflow-build:
	@echo "🐳 Building custom Airflow image..."
	docker build -f src/airflow/Dockerfile -t airflow-ecom:local .
	@echo "📦 Loading image into Kind cluster..."
	kind load docker-image airflow-ecom:local --name ecom-local

nextjs-build:
	@echo "🐳 Building Next.js image..."
	docker build -f src/next_js/Dockerfile -t ecom-nextjs:local src/next_js
	@echo "📦 Loading image into Kind cluster..."
	kind load docker-image ecom-nextjs:local --name ecom-local
	@echo "♻️  Restarting Next.js deployment..."
	kubectl rollout restart deployment/nextjs -n ecom-local
	kubectl rollout status deployment/nextjs -n ecom-local

airflow-apply:
	@echo "🚀 Applying Airflow via Kustomize..."
	kubectl create namespace $(AIRFLOW_NAMESPACE) || true
	kustomize build --enable-helm infrastructure/kubernetes/overlays/local/airflow | kubectl apply -n $(AIRFLOW_NAMESPACE) -f -

airflow-upgrade:
	@echo "⬆️  Upgrading Airflow Helm release..."
	helm upgrade airflow apache-airflow/airflow \
		-n $(AIRFLOW_NAMESPACE) \
		-f infrastructure/kubernetes/overlays/local/airflow/airflow-values.yaml
	kubectl rollout restart statefulset/airflow-scheduler -n $(AIRFLOW_NAMESPACE)

airflow-ui:
	@echo "🌐 Airflow UI → http://localhost:8082"
	kubectl port-forward svc/airflow-api-server 8082:8080 -n $(AIRFLOW_NAMESPACE)

airflow-logs:
	kubectl logs -f deployment/airflow-scheduler -n $(AIRFLOW_NAMESPACE)

airflow-uninstall:
	helm uninstall airflow --namespace $(AIRFLOW_NAMESPACE)
	kubectl delete namespace $(AIRFLOW_NAMESPACE)


# ─────────────────────────────────────
#  Help
# ─────────────────────────────────────

help:
	@echo ""
	@echo "══════════════════════════════════════════"
	@echo "        📊 ECOM DATA PLATFORM"
	@echo "══════════════════════════════════════════"
	@echo ""
	@echo "📦 INSTALLATION"
	@echo "  make install               → Install Poetry dependencies"
	@echo ""
	@echo "🧪 CODE QUALITY"
	@echo "  make test                  → Run all unit tests (CI)"
	@echo "  make test-etl              → Run etl_ecom unit tests only"
	@echo "  make test-mcp              → Run mcp unit tests only"
	@echo "  make lint                  → Lint Python with Ruff"
	@echo "  make lint-sql              → Lint ingestion SQL"
	@echo "  make lint-dbt              → Lint dbt project SQL"
	@echo "  make fix-sql               → Auto-fix ingestion SQL"
	@echo "  make fix-dbt               → Auto-fix dbt SQL"
	@echo ""
	@echo "🌱 DATA SIMULATION"
	@echo "  make seed-daily            → Run daily Postgres seed script"
	@echo "  make simulate-days DAYS=N  → Run seed + ETL for N days"
	@echo ""
	@echo "🚀 PIPELINE"
	@echo "  make run                   → Run the ETL pipeline"
	@echo "  make daily-run             → Daily seed, then ETL"
	@echo "  make full-run              → Daily seed, ETL, then dbt build"
	@echo ""
	@echo "🧱 DBT"
	@echo "  make dbt-run               → Run dbt models"
	@echo "  make dbt-test              → Run dbt tests"
	@echo "  make dbt-build             → dbt run and test"
	@echo "  make dbt-docs              → Generate and serve dbt docs"
	@echo "  make dbt-debug             → Check dbt configuration"
	@echo "  make dbt-seed              → Load dbt seed data"
	@echo "  make dbt-profile           → Open dbt profiles.yml in nano"
	@echo "  make dbt-parse             → Validate dbt DAG, refs, and SQL"
	@echo ""
	@echo "🗄️ DUCKDB INSPECTION"
	@echo "  make schemas               → List all schemas"
	@echo "  make check-tables          → List tables (default schema)"
	@echo "  make tables-schema SCHEMA=metadata → List tables in a schema"
	@echo "  make describe-table TABLE=metadata.etl_watermark → Describe columns"
	@echo "  make count-rows TABLE=metadata.etl_watermark → Count rows"
	@echo "  make preview TABLE=metadata.etl_watermark → Preview last rows"
	@echo "  make last-watermark        → Latest rows from etl_watermark"
	@echo "  make last-metrics          → Latest rows from etl_metrics"
	@echo "  make count-all TABLE=metadata.etl_watermark → Count with SQL alias"
	@echo "  make query SQL='...'       → Run arbitrary SQL"
	@echo "  make db-tree               → Print schema/table tree"
	@echo "  make show-all-tables       → SHOW ALL TABLES via DuckDB"
	@echo ""
	@echo "🧨 MAINTENANCE"
	@echo "  make reset-db              → Delete local DuckDB file"
	@echo "  make reset-db-safe         → Same, with confirmation prompt"
	@echo ""
	@echo "🪣 MINIO"
	@echo "  make minio-buckets         → List buckets on the alias"
	@echo "  make minio-ls              → List objects in the bucket"
	@echo "  make minio-tree            → Recursive tree of the bucket"
	@echo "  make minio-find            → Find objects by pattern"
	@echo "  make minio-cat FILE=...    → Print object contents"
	@echo "  make minio-put FILE=... DEST=... → Upload a file"
	@echo "  make minio-sync DIR=... DEST=... → Mirror a folder to MinIO"
	@echo "  make minio-clean-prefix PREFIX=... → Delete prefix (destructive)"
	@echo ""
	@echo "🧊 ICEBERG"
	@echo "  make iceberg-list-tables                 → List Iceberg tables"
	@echo "  make iceberg-schema TABLE=bronze.users   → Show table schema"
	@echo "  make iceberg-preview TABLE=bronze.users  → Preview rows"
	@echo "  make iceberg-count TABLE=bronze.users    → Row count"
	@echo "  make iceberg-history TABLE=bronze.users  → Snapshot history"
	@echo "  make iceberg-current-snapshot TABLE=...  → Current snapshot id"
	@echo "  make iceberg-drop-table TABLE=...      → Drop one table"
	@echo "  make iceberg-describe TABLE=...        → Describe Iceberg table"
	@echo "  make iceberg-drop-all                    → Drop all Iceberg tables"
	@echo "  make iceberg-snapshots TABLE=...         → List table snapshots"
	@echo ""
	@echo "🔦 TRINO"
	@echo "  make trino                               → Interactive Trino shell"
	@echo "  make trino-catalogs                      → SHOW CATALOGS"
	@echo "  make trino-schemas                       → SHOW SCHEMAS FROM iceberg"
	@echo "  make trino-tables SCHEMA=raw             → SHOW TABLES for a schema"
	@echo "  make trino-preview TABLE=raw.users       → SELECT * LIMIT 10"
	@echo "  make trino-count TABLE=raw.users         → SELECT COUNT(*)"
	@echo "  make trino-describe TABLE=raw.users      → DESCRIBE table"
	@echo "  make trino-show-create TABLE=raw.users   → SHOW CREATE TABLE"
	@echo "  make trino-drop-table TABLE=raw.users    → DROP TABLE"
	@echo "  make trino-drop-schema SCHEMA=raw        → DROP SCHEMA CASCADE"
	@echo "  make trino-query SQL='...'               → Run one SQL statement"
	@echo ""
	@echo "⏩ fastAPI"
	@echo "  make run-api                             → Dev server with reload"
	@echo ""
	@echo "🔭 OBSERVABILITY (Kind)"
	@echo "  make otel-install          → Install Tempo + OTel Collector via Helm"
	@echo "  make otel-uninstall        → Remove Tempo + OTel Collector"
	@echo "  make monitoring-upgrade    → Upgrade kube-prometheus-stack (adds Tempo datasource)"
	@echo ""
	@echo "✈️  AIRFLOW"
	@echo "  make airflow-build         → Build custom image + load into Kind"
	@echo "  make airflow-apply         → Deploy/update Airflow via Kustomize"
	@echo "  make airflow-ui            → Port-forward UI to localhost:8080"
	@echo "  make airflow-logs          → Tail scheduler logs"
	@echo "  make airflow-uninstall     → Remove Airflow from the cluster"
	@echo "══════════════════════════════════════════"
	@echo ""
