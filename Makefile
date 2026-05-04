# ─────────────────────────────────────
#  Variables
# ─────────────────────────────────────
include docker/.env
export
# Chemin vers le dossier dbt (relatif à la racine du projet)
DBT_DIR := src/etl_ecom/transformation

# Commande dbt via Poetry
DBT := poetry run dbt

# Profil : on utilise celui du dossier dbt
# DBT_FLAGS := --profiles-dir $(DBT_DIR)

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
#  Commandes générales du projet
# ─────────────────────────────────────

.PHONY: install lint test run

install:
	@echo "Installation des dépendances Poetry..."
	poetry install

lint:
	@echo "Linting avec ruff..."
	poetry run ruff check src/

test:
	@echo "Lancement des tests..."
	poetry run pytest

run:
	@echo "Lancement de l'application ETL..."
	poetry run python -m src.etl_ecom.pipeline

# ─────────────────────────────────────
#  Raccourcis utiles
# ─────────────────────────────────────

.PHONY: help

help:
	@echo "Commandes disponibles :"
	@echo "  make install       : Installer les dépendances"
	@echo "  make dbt-init      : Initialiser dbt"
	@echo "  make dbt-run       : Exécuter les modèles dbt"
	@echo "  make dbt-test      : Lancer les tests dbt"
	@echo "  make dbt-build     : Run + test"
	@echo "  make dbt-docs      : Ouvrir la documentation"
	@echo "  make dbt-debug     : Vérifier la config dbt"
	@echo "  make dbt-seed      : Charger les seeds"
	@echo "  make lint          : Linter le code"
	@echo "  make test          : Tests unitaires"
	@echo "  make run           : Lancer l'ETL"
	@echo "  make help          : Afficher cette aide"