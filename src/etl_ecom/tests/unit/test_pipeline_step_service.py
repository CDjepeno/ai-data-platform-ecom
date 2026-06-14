from unittest.mock import MagicMock

from etl_ecom.ports.secondary.csv_ingestion_port import CsvIngestionPort
from etl_ecom.ports.secondary.iceberg_loader_port import IcebergLoaderPort
from etl_ecom.ports.secondary.infra_initializer_port import InfraInitializerPort
from etl_ecom.ports.secondary.schema_validator_port import SchemaValidatorPort
from etl_ecom.ports.secondary.semantic_layer_port import SemanticLayerPort
from etl_ecom.ports.secondary.warehouse_state_port import WarehouseStatePort
from etl_ecom.services.pipeline_step_service import PipelineStepService


def make_service(initialized: bool = False) -> tuple:
    warehouse_state = MagicMock(spec=WarehouseStatePort)
    warehouse_state.is_initialized.return_value = initialized
    infra = MagicMock(spec=InfraInitializerPort)
    validator = MagicMock(spec=SchemaValidatorPort)
    loader = MagicMock(spec=IcebergLoaderPort)
    semantic = MagicMock(spec=SemanticLayerPort)
    csv_ingestion = MagicMock(spec=CsvIngestionPort)
    service = PipelineStepService(
        warehouse_state=warehouse_state,
        infra_initializer=infra,
        schema_validator=validator,
        iceberg_loader=loader,
        semantic_layer=semantic,
        csv_ingestion=csv_ingestion,
    )
    return service, infra, validator, loader, semantic, csv_ingestion


class TestPipelineStepService:

    def test_ingest_csv_campaigns_calls_port_with_run_id(self):
        service, _, _, _, _, csv = make_service()

        service.ingest_csv_campaigns("20240101_120000")

        csv.ingest.assert_called_once_with("20240101_120000")

    def test_ingest_csv_campaigns_does_not_affect_other_steps(self):
        service, infra, validator, loader, semantic, _ = make_service()

        service.ingest_csv_campaigns("20240101_120000")

        infra.initialize.assert_not_called()
        validator.validate.assert_not_called()
        loader.load.assert_not_called()
        semantic.build_dbt.assert_not_called()
        semantic.index.assert_not_called()

    def test_initialize_warehouse_skips_when_already_initialized(self):
        service, infra, _, _, _, _ = make_service(initialized=True)

        service.initialize_warehouse()

        infra.initialize.assert_not_called()

    def test_initialize_warehouse_runs_when_not_initialized(self):
        service, infra, _, _, _, _ = make_service(initialized=False)

        service.initialize_warehouse()

        infra.initialize.assert_called_once()
