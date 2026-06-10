from etl_ecom.application.ports.secondary.infra_initializer_port import InfraInitializerPort


class FakeInfraInitializer(InfraInitializerPort):
    def __init__(self):
        self.called = False

    def initialize(self) -> None:
        self.called = True
