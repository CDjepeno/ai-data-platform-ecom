from lang_graph.typing.analytics_state import AnalyticsIntent, SemanticContext
from lang_graph.validator.base_validator import Validator


class MetricsTypeValidator(Validator):

    def validate(
        self,
        intent: AnalyticsIntent,
        context: SemanticContext,
    ) -> AnalyticsIntent:

        metrics = intent["metrics"]

        if not isinstance(metrics, list):

            raise ValueError(
                "Metrics must be a list"
            )

        return intent