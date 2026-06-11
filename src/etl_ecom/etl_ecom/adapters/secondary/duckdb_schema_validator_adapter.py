from duckdb import DuckDBPyConnection

from etl_ecom.application.ports.secondary.schema_validator_port import SchemaValidatorPort
from etl_ecom.ingestion.schema_validation.validate_schema_drift import main as validate_schema_drift


class DuckDbSchemaValidatorAdapter(SchemaValidatorPort):
    def __init__(self, conn: DuckDBPyConnection):
        self._conn = conn

    def validate(self) -> None:
        validate_schema_drift(self._conn)
