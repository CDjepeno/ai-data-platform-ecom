from abc import ABC, abstractmethod


class SemanticLayerPort(ABC):
    @abstractmethod
    def build_dbt(self) -> None: ...

    @abstractmethod
    def index(self) -> None: ...
