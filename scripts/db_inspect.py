#!/usr/bin/env python3
"""Inspection de la base DuckDB"""
import sys
import os

from etl_ecom.db.engine import get_duckdb_connection

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python db_inspect.py <chemin_base> [command] [table|query]")
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists(path):
        print(f"❌ Base de données introuvable : {path}")
        print("   Vérifie que DBT_DUCKDB_PATH_DEV est bien défini")
        sys.exit(1)

    command = sys.argv[2] if len(sys.argv) > 2 else "tables"

    try:
        con = get_duckdb_connection()
    except Exception as e:
        print(f"❌ Erreur de connexion à {path}: {e}")
        sys.exit(1)

    try:
        if command == "schemas":
            print("📂 Schemas dans la base :")
            schemas = con.execute("""
                SELECT DISTINCT schema_name
                FROM information_schema.schemata
                ORDER BY schema_name
            """).fetchall()

            if schemas:
                for s in schemas:
                    print(f"  → {s[0]}")
            else:
                print("  (aucun schema)")
        
        elif command == "tree":
            print("🌳 Structure de la base :")

            query = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name
            """

            rows = con.execute(query).fetchall()

            current_schema = None

            if not rows:
                print("  (aucune table)")
            else:
                for schema, table in rows:
                    if schema != current_schema:
                        print(f"\n📂 {schema}")
                        current_schema = schema
                    print(f"  ├── {table}")

        # 🔥 NOUVEAU : tables par schema
        elif command == "tables_schema":
            schema = sys.argv[3] if len(sys.argv) > 3 else "main"
            print(f"📊 Tables dans le schema '{schema}' :")
            try:
                tables = con.execute(f"SHOW TABLES FROM {schema}").fetchall()
                if tables:
                    for t in tables:
                        print(f"  → {t[0]}")
                else:
                    print("  (aucune table)")
            except Exception as e:
                print(f"  ❌ Erreur: {e}")

        elif command == "tables":
            print("📊 Tables dans la base :")
            tables = con.execute("SHOW TABLES").fetchall()
            if tables:
                for t in tables:
                    print(f"  → {t[0]}")
            else:
                print("  (aucune table)")

        elif command == "describe":
            table = sys.argv[3] if len(sys.argv) > 3 else "etl_metrics"
            print(f"📋 Structure de {table} :")
            try:
                cols = con.execute(f"DESCRIBE {table}").fetchall()
                for c in cols:
                    print(f"  • {c[0]} : {c[1]}")
            except Exception as e:
                print(f"  ❌ Table {table} introuvable: {e}")

        elif command == "count":
            table = sys.argv[3] if len(sys.argv) > 3 else "etl_metrics"
            print(f"📊 Comptage des lignes de {table}...")
            try:
                result = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                if result is not None:
                    count = result[0]
                    print(f"  ✅ {count} lignes")
                else:
                    print(f"  ⚠️  Table vide ou inexistante")
            except Exception as e:
                print(f"  ❌ Erreur: {e}")

        elif command == "query":
            if len(sys.argv) < 4:
                print("❌ Usage: python db_inspect.py <path> query <SQL>")
                sys.exit(1)
            query = sys.argv[3]
            print(f"🔍 Exécution de : {query}")
            try:
                result = con.execute(query).fetchdf()
                print(result)
            except Exception as e:
                print(f"  ❌ Erreur SQL: {e}")

    finally:
        con.close()

if __name__ == "__main__":
    main()