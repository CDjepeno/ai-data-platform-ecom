from etl_ecom.db.db_config import settings
from etl_ecom.db.engine import get_duckdb_connection
from etl_ecom.adapters.secondary.duckdb_warehouse_state import DuckDbWarehouseState
from etl_ecom.adapters.secondary.default_infra_initializer import DefaultInfraInitializer
from etl_ecom.adapters.secondary.duckdb_schema_validator import DuckDbSchemaValidator
from etl_ecom.adapters.secondary.minio_iceberg_loader import MinioIcebergLoader
from etl_ecom.adapters.secondary.http_semantic_layer import HttpSemanticLayer
from etl_ecom.application.use_cases.run_pipeline_use_case import RunPipelineUseCase


class PipelineFactory:
    @staticmethod
    def create() -> RunPipelineUseCase:
        conn = get_duckdb_connection()
        return RunPipelineUseCase(
            warehouse_state=DuckDbWarehouseState(conn),
            infra_initializer=DefaultInfraInitializer(),
            schema_validator=DuckDbSchemaValidator(conn),
            iceberg_loader=MinioIcebergLoader(conn),
            semantic_layer=HttpSemanticLayer(settings.semantic_layer_url),
        )
