from etl_ecom.application.ports.primary.run_pipeline_port import RunPipelinePort
from etl_ecom.application.ports.secondary.warehouse_state_port import WarehouseStatePort
from etl_ecom.application.ports.secondary.infra_initializer_port import InfraInitializerPort
from etl_ecom.application.ports.secondary.schema_validator_port import SchemaValidatorPort
from etl_ecom.application.ports.secondary.iceberg_loader_port import IcebergLoaderPort
from etl_ecom.application.ports.secondary.semantic_layer_port import SemanticLayerPort
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


class RunPipelineUseCase(RunPipelinePort):
    def __init__(
        self,
        warehouse_state: WarehouseStatePort,
        infra_initializer: InfraInitializerPort,
        schema_validator: SchemaValidatorPort,
        iceberg_loader: IcebergLoaderPort,
        semantic_layer: SemanticLayerPort,
    ):
        self._warehouse_state = warehouse_state
        self._infra_initializer = infra_initializer
        self._schema_validator = schema_validator
        self._iceberg_loader = iceberg_loader
        self._semantic_layer = semantic_layer

    def execute(self, run_id: str) -> None:
        if self._warehouse_state.is_initialized():
            logger.info("✅ Warehouse already initialized")
            return

        logger.info("🚀 Starting Pipeline")

        self._infra_initializer.initialize()
        self._schema_validator.validate()
        self._iceberg_loader.load(run_id)
        self._semantic_layer.build_dbt()
        self._semantic_layer.index()

        logger.info("🏁 Pipeline finished 🌞")
