

from lang_graph.typing.analytics_state import AnalyticsIntent, SemanticContext
from lang_graph.validator.base_validator import Validator


class RequiredFieldsValidator(Validator):

    def validate(
        self,
        intent: AnalyticsIntent,
        context: SemanticContext,
    ) -> AnalyticsIntent:

        required_fields = [
            "metrics",
        ]

        for field in required_fields:

            if field not in intent:

                raise ValueError(
                    f"Missing required field: {field}"
                )

        return intent