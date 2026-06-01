from etl_ecom.scripts.iceberg.iceberg import get_iceberg_catalog

catalog = get_iceberg_catalog()

print("🧨 Dropping all Iceberg tables...\n")

namespaces = catalog.list_namespaces()

for namespace in namespaces:
    print(f"📂 Namespace: {namespace}")

    tables = catalog.list_tables(namespace)

    if not tables:
        print("   └── (empty)")
        continue

    for table_identifier in tables:
        try:
            catalog.drop_table(table_identifier)

            print(f"   └── ❌ Dropped: {table_identifier}")

        except Exception as e:
            print(f"   └── ⚠️ Failed: {table_identifier} -> {e}")

print("\n✅ Done")
