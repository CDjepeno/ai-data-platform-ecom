from datetime import datetime

from pyarrow import Table
import pyarrow as pa

from scripts.iceberg.iceberg import get_iceberg_catalog

catalog = get_iceberg_catalog()

table = catalog.load_table("bronze.users")

schema = pa.schema([
    pa.field("id", pa.int64(), nullable=False),
    pa.field("email", pa.string()),
    pa.field("created_at", pa.timestamp("us")),
])

data = pa.Table.from_pydict(
    {
        "id": [1, 2],
        "email": ["a@test.com", "b@test.com"],
        "created_at": [datetime.now(), datetime.now()],
    },
    schema=schema,
)

table.append(data)

print("✅ data appended")