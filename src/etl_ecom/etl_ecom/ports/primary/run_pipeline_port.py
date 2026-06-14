from abc import ABC, abstractmethod


class RunPipelinePort(ABC):
    @abstractmethod
    def execute(self, run_id: str) -> None: ...
