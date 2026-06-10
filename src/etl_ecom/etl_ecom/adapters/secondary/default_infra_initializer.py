from etl_ecom.application.ports.secondary.infra_initializer_port import InfraInitializerPort
from etl_ecom.ingestion.initialize_infra import initialize_infra


class DefaultInfraInitializer(InfraInitializerPort):
    def initialize(self) -> None:
        initialize_infra()
