from lang_graph.typing.analytics_state import AnalyticsIntent, SemanticContext
from lang_graph.validator.base_validator import Validator


class DuplicateMetricValidator(Validator):

    def validate(
        self,
        intent: AnalyticsIntent,
        context: SemanticContext,
    ) -> AnalyticsIntent:

        intent["metrics"] = list(
            set(intent["metrics"])
        )

        return intent