#!/usr/bin/env python3
"""Inspect the DuckDB database."""
import sys
import os

from etl_ecom.db.engine import get_duckdb_connection

def main():
    if len(sys.argv) < 2:
        print("❌ Usage: python db_inspect.py <database_path> [command] [table|query]")
        sys.exit(1)

    path = sys.argv[1]

    if not os.path.exists(path):
        print(f"❌ Database not found: {path}")
        print("   Make sure DBT_DUCKDB_PATH_DEV is set correctly")
        sys.exit(1)

    command = sys.argv[2] if len(sys.argv) > 2 else "tables"

    try:
        con = get_duckdb_connection()
    except Exception as e:
        print(f"❌ Connection error for {path}: {e}")
        sys.exit(1)

    try:
        if command == "schemas":
            print("📂 Schemas in the database:")
            schemas = con.execute("""
                SELECT DISTINCT schema_name
                FROM information_schema.schemata
                ORDER BY schema_name
            """).fetchall()

            if schemas:
                for s in schemas:
                    print(f"  → {s[0]}")
            else:
                print("  (no schemas)")

        elif command == "tree":
            print("🌳 Database structure:")

            query = """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name
            """

            rows = con.execute(query).fetchall()

            current_schema = None

            if not rows:
                print("  (no tables)")
            else:
                for schema, table in rows:
                    if schema != current_schema:
                        print(f"\n📂 {schema}")
                        current_schema = schema
                    print(f"  ├── {table}")

        # Tables listed by schema
        elif command == "tables_schema":
            schema = sys.argv[3] if len(sys.argv) > 3 else "main"
            print(f"📊 Tables in schema '{schema}':")
            try:
                tables = con.execute(f"SHOW TABLES FROM {schema}").fetchall()
                if tables:
                    for t in tables:
                        print(f"  → {t[0]}")
                else:
                    print("  (no tables)")
            except Exception as e:
                print(f"  ❌ Error: {e}")

        elif command == "tables":
            print("📊 Tables in the database:")
            tables = con.execute("SHOW TABLES").fetchall()
            if tables:
                for t in tables:
                    print(f"  → {t[0]}")
            else:
                print("  (no tables)")

        elif command == "describe":
            table = sys.argv[3] if len(sys.argv) > 3 else "etl_metrics"
            print(f"📋 Structure of {table}:")
            try:
                cols = con.execute(f"DESCRIBE {table}").fetchall()
                for c in cols:
                    print(f"  • {c[0]} : {c[1]}")
            except Exception as e:
                print(f"  ❌ Table {table} not found: {e}")

        elif command == "count":
            table = sys.argv[3] if len(sys.argv) > 3 else "etl_metrics"
            print(f"📊 Row count for {table}...")
            try:
                result = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
                if result is not None:
                    count = result[0]
                    print(f"  ✅ {count} rows")
                else:
                    print("  ⚠️  Empty or missing table")
            except Exception as e:
                print(f"  ❌ Error: {e}")

        elif command == "query":
            if len(sys.argv) < 4:
                print("❌ Usage: python db_inspect.py <path> query <SQL>")
                sys.exit(1)
            query = sys.argv[3]
            print(f"🔍 Running: {query}")
            try:
                result = con.execute(query).fetchdf()
                print(result)
            except Exception as e:
                print(f"  ❌ SQL error: {e}")

    finally:
        con.close()

if __name__ == "__main__":
    main()
