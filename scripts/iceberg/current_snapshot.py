import sys

from etl_ecom.db.iceberg import get_iceberg_catalog

if len(sys.argv) < 2:
    print("❌ Usage: python current_snapshot.py bronze.users")
    sys.exit(1)

table_name = sys.argv[1]

catalog = get_iceberg_catalog()

table = catalog.load_table(table_name)

snapshot = table.current_snapshot()

if snapshot is None:
    print(f"❌ Aucun snapshot trouvé pour {table_name}")
    sys.exit(1)

print(f"\n🧊 Current Snapshot: {table_name}\n")

print(f"Snapshot ID : {snapshot.snapshot_id}")
print(f"Timestamp   : {snapshot.timestamp_ms}")
print(f"Manifest    : {snapshot.manifest_list}")