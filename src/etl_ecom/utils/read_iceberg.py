
from etl_ecom.db.iceberg import get_iceberg_catalog


catalog = get_iceberg_catalog()

table = catalog.load_table("bronze.users")

df = table.scan().to_pandas()

print(df)