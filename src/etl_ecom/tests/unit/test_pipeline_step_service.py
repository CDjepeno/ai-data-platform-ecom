import pytest

from etl_ecom.services.pipeline_step_service import PipelineStepService
from tests.fakes.fake_warehouse_state import FakeWarehouseState
from tests.fakes.fake_infra_initializer import FakeInfraInitializer
from tests.fakes.fake_schema_validator import FakeSchemaValidator
from tests.fakes.fake_iceberg_loader import FakeIcebergLoader
from tests.fakes.fake_semantic_layer import FakeSemanticLayer
from tests.fakes.fake_csv_ingestion import FakeCsvIngestion


def make_service(
    initialized: bool = False,
    csv_rows: int = 33,
) -> tuple:
    infra = FakeInfraInitializer()
    validator = FakeSchemaValidator()
    loader = FakeIcebergLoader()
    semantic = FakeSemanticLayer()
    csv_ingestion = FakeCsvIngestion(csv_rows)
    service = PipelineStepService(
        warehouse_state=FakeWarehouseState(initialized),
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

        assert csv.called_with == "20240101_120000"

    def test_ingest_csv_campaigns_does_not_affect_other_steps(self):
        service, infra, validator, loader, semantic, _ = make_service()

        service.ingest_csv_campaigns("20240101_120000")

        assert not infra.called
        assert not validator.called
        assert loader.called_with is None
        assert not semantic.dbt_built
        assert not semantic.indexed

    def test_initialize_warehouse_skips_when_already_initialized(self):
        service, infra, _, _, _, _ = make_service(initialized=True)

        service.initialize_warehouse()

        assert not infra.called

    def test_initialize_warehouse_runs_when_not_initialized(self):
        service, infra, _, _, _, _ = make_service(initialized=False)

        service.initialize_warehouse()

        assert infra.called
