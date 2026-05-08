import sys

from etl_ecom.db.iceberg import get_iceberg_catalog

table_name = sys.argv[1]

catalog = get_iceberg_catalog()
table = catalog.load_table(table_name)

print("\n📸 SNAPSHOTS\n")

for snapshot in table.metadata.snapshots:
    print(snapshot)