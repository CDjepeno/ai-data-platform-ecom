from abc import ABC, abstractmethod


class InfraInitializerPort(ABC):
    @abstractmethod
    def initialize(self) -> None: ...
