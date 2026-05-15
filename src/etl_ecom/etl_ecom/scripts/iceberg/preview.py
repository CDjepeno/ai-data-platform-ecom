from sys import argv

from etl_ecom.utils.logger import get_logger
from etl_ecom.scripts.iceberg.iceberg import get_iceberg_catalog

logger = get_logger(__name__)


def main():
    table_name = argv[1]

    catalog = get_iceberg_catalog()

    table = catalog.load_table(table_name)

    df = table.scan().to_arrow().to_pandas()

    logger.info(df.head(20))


if __name__ == "__main__":
    main()
