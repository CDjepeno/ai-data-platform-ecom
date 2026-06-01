import pyarrow as pa
from pyiceberg.schema import Schema
from pyiceberg.types import (
    BooleanType,
    DateType,
    DecimalType,
    DoubleType,
    IntegerType,
    LongType,
    NestedField,
    StringType,
    TimestampType,
)

from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


def arrow_to_iceberg_schema(arrow_schema):

    fields = []

    for idx, field in enumerate(arrow_schema, start=1):

        field_type = field.type

        if pa.types.is_int64(field_type):
            iceberg_type = LongType()

        elif pa.types.is_int32(field_type):
            iceberg_type = IntegerType()

        elif pa.types.is_string(field_type):
            iceberg_type = StringType()

        elif pa.types.is_timestamp(field_type):
            iceberg_type = TimestampType()

        elif pa.types.is_boolean(field_type):
            iceberg_type = BooleanType()

        elif pa.types.is_floating(field_type):
            iceberg_type = DoubleType()

        elif pa.types.is_timestamp(field_type):
            iceberg_type = TimestampType()

        elif pa.types.is_date(field_type):
            iceberg_type = DateType()

        elif pa.types.is_decimal(field_type):
            iceberg_type = DecimalType(
                precision=field_type.precision, scale=field_type.scale
            )

        elif pa.types.is_boolean(field_type):
            iceberg_type = BooleanType()

        # ENUM postgres / dictionary
        elif pa.types.is_dictionary(field_type):
            iceberg_type = StringType()

        else:
            logger.warning(f"⚠️ Type inconnu {field_type}, fallback STRING")
            iceberg_type = StringType()

        fields.append(
            NestedField(
                field_id=idx,
                name=field.name,
                field_type=iceberg_type,
                required=False,
            )
        )

    return Schema(*fields)
