import sys

from etl_ecom.scripts.iceberg.iceberg import get_iceberg_catalog


def main():

    if len(sys.argv) < 2:
        print("❌ Usage: python count.py bronze.users")
        sys.exit(1)

    table_name = sys.argv[1]

    catalog = get_iceberg_catalog()

    table = catalog.load_table(table_name)

    row_count = table.scan().to_arrow().num_rows

    print(f"\n🧊 Table: {table_name}")
    print(f"📊 Rows: {row_count}")


if __name__ == "__main__":
    main()
