import pytest
from unittest.mock import MagicMock

from etl_ecom.ports.secondary.csv_ingestion_port import CsvIngestionPort
from etl_ecom.ports.secondary.iceberg_loader_port import IcebergLoaderPort
from etl_ecom.ports.secondary.infra_initializer_port import InfraInitializerPort
from etl_ecom.ports.secondary.schema_validator_port import SchemaValidatorPort
from etl_ecom.ports.secondary.semantic_layer_port import SemanticLayerPort
from etl_ecom.ports.secondary.warehouse_state_port import WarehouseStatePort
from etl_ecom.application.use_cases.run_pipeline_use_case import RunPipelineUseCase


def make_use_case(
    initialized: bool = False,
    schema_raises: bool = False,
    rows_loaded: int = 10,
) -> tuple:
    warehouse_state = MagicMock(spec=WarehouseStatePort)
    warehouse_state.is_initialized.return_value = initialized
    infra = MagicMock(spec=InfraInitializerPort)
    validator = MagicMock(spec=SchemaValidatorPort)
    if schema_raises:
        validator.validate.side_effect = Exception("Schema drift detected")
    loader = MagicMock(spec=IcebergLoaderPort)
    loader.load.return_value = rows_loaded
    semantic = MagicMock(spec=SemanticLayerPort)
    csv_ingestion = MagicMock(spec=CsvIngestionPort)
    use_case = RunPipelineUseCase(
        warehouse_state=warehouse_state,
        infra_initializer=infra,
        schema_validator=validator,
        iceberg_loader=loader,
        semantic_layer=semantic,
        csv_ingestion=csv_ingestion,
    )
    return use_case, infra, validator, loader, semantic, csv_ingestion


class TestRunPipelineUseCase:

    def test_full_pipeline_runs_all_steps(self):
        use_case, infra, validator, loader, semantic, csv = make_use_case()

        use_case.execute("20240101_120000")

        infra.initialize.assert_called_once()
        validator.validate.assert_called_once()
        loader.load.assert_called_once_with("20240101_120000")
        csv.ingest.assert_called_once_with("20240101_120000")
        semantic.build_dbt.assert_called_once()
        semantic.index.assert_called_once()

    def test_skips_pipeline_when_already_initialized(self):
        use_case, infra, validator, loader, semantic, csv = make_use_case(initialized=True)

        use_case.execute("20240101_120000")

        infra.initialize.assert_not_called()
        validator.validate.assert_not_called()
        loader.load.assert_not_called()
        csv.ingest.assert_not_called()
        semantic.build_dbt.assert_not_called()
        semantic.index.assert_not_called()

    def test_raises_and_stops_when_schema_drift_detected(self):
        # validate() now runs AFTER load() — drift detection blocks dbt, not the load.
        use_case, _, _, loader, semantic, csv = make_use_case(schema_raises=True)

        with pytest.raises(Exception, match="Schema drift detected"):
            use_case.execute("20240101_120000")

        loader.load.assert_called_once_with("20240101_120000")
        csv.ingest.assert_called_once_with("20240101_120000")
        semantic.build_dbt.assert_not_called()
        semantic.index.assert_not_called()
