from etl_ecom.application.ports.secondary.warehouse_state_port import WarehouseStatePort


class FakeWarehouseState(WarehouseStatePort):
    def __init__(self, initialized: bool = False):
        self._initialized = initialized

    def is_initialized(self) -> bool:
        return self._initialized
