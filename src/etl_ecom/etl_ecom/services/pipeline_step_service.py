from etl_ecom.application.ports.secondary.infra_initializer_port import InfraInitializerPort
from etl_ecom.application.ports.secondary.schema_validator_port import SchemaValidatorPort
from etl_ecom.application.ports.secondary.iceberg_loader_port import IcebergLoaderPort
from etl_ecom.application.ports.secondary.semantic_layer_port import SemanticLayerPort
from etl_ecom.application.ports.secondary.warehouse_state_port import WarehouseStatePort
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


class PipelineStepService:
    """
    Executes individual pipeline steps.
    Each method has one responsibility and receives
    its dependency via constructor injection — no instantiation here.
    """

    def __init__(
        self,
        warehouse_state: WarehouseStatePort,
        infra_initializer: InfraInitializerPort,
        schema_validator: SchemaValidatorPort,
        iceberg_loader: IcebergLoaderPort,
        semantic_layer: SemanticLayerPort,
    ) -> None:
        self._warehouse_state = warehouse_state
        self._infra_initializer = infra_initializer
        self._schema_validator = schema_validator
        self._iceberg_loader = iceberg_loader
        self._semantic_layer = semantic_layer

    def initialize_warehouse(self) -> None:
        if self._warehouse_state.is_initialized():
            logger.info("✅ Warehouse already initialized, skipping")
            return
        self._infra_initializer.initialize()

    def validate_schema(self) -> None:
        self._schema_validator.validate()

    def load_to_iceberg(self, run_id: str) -> None:
        self._iceberg_loader.load(run_id)

    def build_dbt(self) -> None:
        self._semantic_layer.build_dbt()

    def index_semantic_layer(self) -> None:
        self._semantic_layer.index()