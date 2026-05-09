import sys

from scripts.iceberg.iceberg import get_iceberg_catalog

if len(sys.argv) < 2:
    print("❌ Usage: python schema.py bronze.users")
    sys.exit(1)

table_name = sys.argv[1]

catalog = get_iceberg_catalog()

table = catalog.load_table(table_name)

print(f"\n🧊 Schema: {table_name}\n")

print(table.schema())