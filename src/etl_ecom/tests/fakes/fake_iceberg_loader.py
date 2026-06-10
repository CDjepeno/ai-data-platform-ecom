from etl_ecom.application.ports.secondary.iceberg_loader_port import IcebergLoaderPort


class FakeIcebergLoader(IcebergLoaderPort):
    def __init__(self, rows_loaded: int = 10):
        self.called_with: str | None = None
        self._rows_loaded = rows_loaded

    def load(self, run_id: str) -> int:
        self.called_with = run_id
        return self._rows_loaded
