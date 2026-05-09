from sys import argv

from scripts.iceberg.iceberg import get_iceberg_catalog


def main():
    table_name = argv[1]

    catalog = get_iceberg_catalog()

    table = catalog.load_table(table_name)

    print("\n📦 LOCATION")
    print(table.location())

    print("\n🧊 SCHEMA")
    print(table.schema())

    print("\n📊 CURRENT SNAPSHOT")
    print(table.current_snapshot())

    print("\n📝 PROPERTIES")
    print(table.properties)


if __name__ == "__main__":
    main()