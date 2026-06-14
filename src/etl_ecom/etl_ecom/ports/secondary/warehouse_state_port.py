from abc import ABC, abstractmethod


class WarehouseStatePort(ABC):
    @abstractmethod
    def is_initialized(self) -> bool: ...
