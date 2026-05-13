from difflib import get_close_matches


from lang_graph.helper.semantic_helper import extract_metric_names
from lang_graph.typing.analytics_state import AnalyticsIntent, SemanticContext
from lang_graph.validator.base_validator import (
    Validator,
)


class FuzzyMetricValidator(Validator):

    def validate(
        self,
        intent: AnalyticsIntent,
        context: SemanticContext,
    ) -> AnalyticsIntent:

        available_metrics = extract_metric_names(
            context
        )

        normalized_metrics = []

        for metric in intent["metrics"]:

            # ✅ Exact match
            if metric in available_metrics:

                normalized_metrics.append(metric)

                continue

            # 🔎 Fuzzy match
            close_matches = get_close_matches(
                metric,
                available_metrics,
                n=1,
                cutoff=0.6,
            )

            if not close_matches:

                raise ValueError(
                    f"No close metric found for {metric}"
                )

            normalized_metrics.append(
                close_matches[0]
            )

        intent["metrics"] = normalized_metrics

        return intent