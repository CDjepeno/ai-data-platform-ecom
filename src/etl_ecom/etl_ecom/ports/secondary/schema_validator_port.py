from abc import ABC, abstractmethod


class SchemaValidatorPort(ABC):
    @abstractmethod
    def validate(self) -> None: ...
