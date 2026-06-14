"""Drop all Iceberg tables in dbt-managed namespaces (mart, ecom, snapshots).

Use this when dbt reports ICEBERG_MISSING_METADATA or a snapshot is missing
SCD columns (dbt_scd_id, dbt_valid_from, dbt_valid_to) — Nessie holds stale
entries whose metadata files no longer exist in MinIO, or whose schema predates
the dbt snapshot config. Dropping them lets dbt recreate the tables cleanly.

Raw tables (raw.*) are intentionally preserved so the full ETL re-run is
not required — Airbyte Parquet files in MinIO are still valid.
"""

from etl_ecom.scripts.iceberg.iceberg import get_iceberg_catalog

DBT_NAMESPACES = {"mart", "ecom", "snapshots"}

catalog = get_iceberg_catalog()

print("🧨 Dropping stale dbt Iceberg tables...\n")

for namespace in catalog.list_namespaces():
    ns_name = namespace[0]
    if ns_name not in DBT_NAMESPACES:
        print(f"⏭️  Skipping namespace: {ns_name} (not dbt-managed)")
        continue

    print(f"📂 Namespace: {ns_name}")
    tables = catalog.list_tables(namespace)

    if not tables:
        print("   └── (empty)")
        continue

    for table_identifier in tables:
        try:
            catalog.drop_table(table_identifier)
            print(f"   └── ❌ Dropped: {table_identifier}")
        except Exception as e:
            print(f"   └── ⚠️  Failed: {table_identifier} → {e}")

print("\n✅ Done — re-trigger the semantic layer build to recreate dbt tables")
