from abc import ABC, abstractmethod

from lang_graph.typing.analytics_state import AnalyticsIntent, SemanticContext


class Validator(ABC):

    @abstractmethod
    def validate(
        self,
        intent: AnalyticsIntent,
        context: SemanticContext,
    ) -> dict:
        pass