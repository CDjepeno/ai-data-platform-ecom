from duckdb import DuckDBPyConnection

from etl_ecom.ports.secondary.warehouse_state_port import WarehouseStatePort
from etl_ecom.warehouse.warehouse_initialized import warehouse_initialized


class DuckDbWarehouseStateAdapter(WarehouseStatePort):
    def __init__(self, conn: DuckDBPyConnection):
        self._conn = conn

    def is_initialized(self) -> bool:
        return warehouse_initialized(self._conn)
