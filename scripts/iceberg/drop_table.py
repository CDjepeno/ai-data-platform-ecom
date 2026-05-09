import sys

from scripts.iceberg.iceberg import get_iceberg_catalog

if len(sys.argv) < 2:
    print("❌ Usage: python drop_table.py bronze.users")
    sys.exit(1)

table_name = sys.argv[1]

catalog = get_iceberg_catalog()

try:
    catalog.drop_table(table_name)
    print(f"🧨 Table dropped: {table_name}")

except Exception as e:
    print(f"❌ Error dropping table: {e}")