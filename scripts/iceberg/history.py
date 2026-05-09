import sys

from scripts.iceberg.iceberg import get_iceberg_catalog

if len(sys.argv) < 2:
    print("❌ Usage: python history.py bronze.users")
    sys.exit(1)

table_name = sys.argv[1]

catalog = get_iceberg_catalog()

table = catalog.load_table(table_name)

print(f"\n📜 Snapshot history: {table_name}\n")

for history in table.history():
    print(history)