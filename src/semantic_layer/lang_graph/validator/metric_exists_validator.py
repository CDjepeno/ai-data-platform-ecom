
from lang_graph.helper.semantic_helper import extract_metric_names
from lang_graph.typing.analytics_state import AnalyticsIntent, SemanticContext
from lang_graph.validator.base_validator import Validator


class MetricExistsValidator(Validator):

    def validate(
        self,
        intent: AnalyticsIntent,
        context: SemanticContext,
    ) -> AnalyticsIntent:

        requested_metrics = intent["metrics"]

        available_metrics = extract_metric_names(
            context
        )

        invalid_metrics = [
            metric
            for metric in requested_metrics
            if metric not in available_metrics
        ]

        if invalid_metrics:

            raise ValueError(
                f"Invalid metrics: "
                f"{invalid_metrics}"
            )

        return intent