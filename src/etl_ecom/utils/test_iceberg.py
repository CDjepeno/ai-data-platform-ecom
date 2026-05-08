from pyiceberg.schema import Schema
from pyiceberg.types import LongType, NestedField, StringType, TimestampType

from etl_ecom.db.iceberg import get_iceberg_catalog

catalog = get_iceberg_catalog()


# =========================
# CREATE NAMESPACE
# =========================

try:
    catalog.create_namespace("bronze")
    print("✅ namespace created")

except Exception:
    print("ℹ️ namespace already exists")

# =========================
# SCHEMA
# =========================

schema = Schema(
    NestedField(1, "id", LongType(), required=True),
    NestedField(2, "email", StringType(), required=False),
    NestedField(3, "created_at", TimestampType(), required=False),
)

table = catalog.create_table(
    identifier="bronze.users",
    schema=schema,
)

print("✅ table created")