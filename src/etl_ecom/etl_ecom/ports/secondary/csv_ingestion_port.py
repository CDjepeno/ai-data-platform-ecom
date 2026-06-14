from abc import ABC, abstractmethod


class CsvIngestionPort(ABC):
    @abstractmethod
    def ingest(self, run_id: str) -> int: ...
