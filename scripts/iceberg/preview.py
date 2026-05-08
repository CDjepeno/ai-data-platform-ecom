from sys import argv

from etl_ecom.db.iceberg import get_iceberg_catalog


def main():
    table_name = argv[1]

    catalog = get_iceberg_catalog()

    table = catalog.load_table(table_name)

    df = table.scan().to_arrow().to_pandas()

    print(df.head(20))


if __name__ == "__main__":
    main()