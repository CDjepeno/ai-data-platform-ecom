from etl_ecom.ports.secondary.infra_initializer_port import InfraInitializerPort
from etl_ecom.ingestion.initialize_infra import initialize_infra


class DefaultInfraInitializerAdapter(InfraInitializerPort):
    def initialize(self) -> None:
        initialize_infra()
