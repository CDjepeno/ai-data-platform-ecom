import pytest

from etl_ecom.application.use_cases.run_pipeline_use_case import RunPipelineUseCase
from tests.fakes.fake_warehouse_state import FakeWarehouseState
from tests.fakes.fake_infra_initializer import FakeInfraInitializer
from tests.fakes.fake_schema_validator import FakeSchemaValidator
from tests.fakes.fake_iceberg_loader import FakeIcebergLoader
from tests.fakes.fake_semantic_layer import FakeSemanticLayer
from tests.fakes.fake_csv_ingestion import FakeCsvIngestion


def make_use_case(
    initialized: bool = False,
    schema_raises: bool = False,
    rows_loaded: int = 10,
    csv_rows: int = 33,
) -> tuple:
    infra = FakeInfraInitializer()
    validator = FakeSchemaValidator(schema_raises)
    loader = FakeIcebergLoader(rows_loaded)
    semantic = FakeSemanticLayer()
    csv_ingestion = FakeCsvIngestion(csv_rows)
    use_case = RunPipelineUseCase(
        warehouse_state=FakeWarehouseState(initialized),
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

        assert infra.called
        assert validator.called
        assert loader.called_with == "20240101_120000"
        assert csv.called_with == "20240101_120000"
        assert semantic.dbt_built
        assert semantic.indexed

    def test_skips_pipeline_when_already_initialized(self):
        use_case, infra, validator, loader, semantic, csv = make_use_case(initialized=True)

        use_case.execute("20240101_120000")

        assert not infra.called
        assert not validator.called
        assert loader.called_with is None
        assert csv.called_with is None
        assert not semantic.dbt_built
        assert not semantic.indexed

    def test_raises_and_stops_when_schema_drift_detected(self):
        use_case, _, _, loader, semantic, csv = make_use_case(schema_raises=True)

        with pytest.raises(Exception, match="Schema drift detected"):
            use_case.execute("20240101_120000")

        assert loader.called_with is None
        assert csv.called_with is None
        assert not semantic.dbt_built
        assert not semantic.indexed
