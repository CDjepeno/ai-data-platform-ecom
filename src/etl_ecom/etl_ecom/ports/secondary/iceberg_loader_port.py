from abc import ABC, abstractmethod


class IcebergLoaderPort(ABC):
    @abstractmethod
    def load(self, run_id: str) -> int: ...
