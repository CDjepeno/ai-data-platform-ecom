from etl_ecom.application.ports.secondary.csv_ingestion_port import CsvIngestionPort


class FakeCsvIngestion(CsvIngestionPort):
    def __init__(self, rows: int = 33):
        self.called_with: str | None = None
        self._rows = rows

    def ingest(self, run_id: str) -> int:
        self.called_with = run_id
        return self._rows
