from scripts.iceberg.iceberg import get_iceberg_catalog

catalog = get_iceberg_catalog()

print("\n🧊 ICEBERG TABLES\n")

for namespace in catalog.list_namespaces():
    print(f"📂 Namespace: {namespace}")

    for table in catalog.list_tables(namespace):
        print(f"   └── {table}")

    print()