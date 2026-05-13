from lang_graph.typing.analytics_state import AnalyticsIntent, SemanticContext
from lang_graph.validator.base_validator import Validator


class EmptyMetricValidator(Validator):

    def validate(
        self,
        intent: AnalyticsIntent,
        context: SemanticContext,
    ) -> AnalyticsIntent:

        if not intent["metrics"]:

            raise ValueError(
                "No metrics requested"
            )

        return intent