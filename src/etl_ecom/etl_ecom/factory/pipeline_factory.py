from pathlib import Path

from etl_ecom.application.use_cases.run_pipeline_use_case import RunPipelineUseCase
from etl_ecom.db.db_config import settings
from etl_ecom.db.engine import get_duckdb_connection
from etl_ecom.adapters.secondary.duckdb_warehouse_state_adapter import DuckDbWarehouseStateAdapter
from etl_ecom.adapters.secondary.default_infra_initializer_adapter import DefaultInfraInitializerAdapter
from etl_ecom.adapters.secondary.duckdb_schema_validator_adapter import DuckDbSchemaValidatorAdapter
from etl_ecom.adapters.secondary.minio_iceberg_loader_adapter import MinioIcebergLoaderAdapter
from etl_ecom.adapters.secondary.http_semantic_layer_adapter import HttpSemanticLayerAdapter
from etl_ecom.adapters.secondary.duckdb_csv_ingestion_adapter import DuckdbCsvIngestionAdapter
from etl_ecom.services.pipeline_step_service import PipelineStepService

_CSV_DIR = Path(__file__).parent.parent.parent / "data" / "campaigns"


class PipelineFactory:

    @staticmethod
    def create_use_case() -> RunPipelineUseCase:
        """Full pipeline — used by scripts and tests."""
        conn = get_duckdb_connection()
        return RunPipelineUseCase(
            warehouse_state=DuckDbWarehouseStateAdapter(conn),
            infra_initializer=DefaultInfraInitializerAdapter(),
            schema_validator=DuckDbSchemaValidatorAdapter(conn),
            iceberg_loader=MinioIcebergLoaderAdapter(conn),
            semantic_layer=HttpSemanticLayerAdapter(settings.semantic_layer_url),
            csv_ingestion=DuckdbCsvIngestionAdapter(conn, _CSV_DIR),
        )
    
    @staticmethod
    def create_step_service() -> PipelineStepService:
        conn = get_duckdb_connection()
        return PipelineStepService(
            warehouse_state=DuckDbWarehouseStateAdapter(conn),
            infra_initializer=DefaultInfraInitializerAdapter(),
            schema_validator=DuckDbSchemaValidatorAdapter(conn),
            iceberg_loader=MinioIcebergLoaderAdapter(conn),
            semantic_layer=HttpSemanticLayerAdapter(settings.semantic_layer_url),
            csv_ingestion=DuckdbCsvIngestionAdapter(conn, _CSV_DIR),
        )
