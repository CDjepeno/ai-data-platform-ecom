from lang_graph.helper.semantic_helper import extract_dimension_names
from lang_graph.typing.analytics_state import AnalyticsIntent, SemanticContext
from lang_graph.validator.base_validator import Validator


class DimensionExistsValidator(Validator):

    def validate(
        self,
        intent: AnalyticsIntent,
        context: SemanticContext,
    ) -> AnalyticsIntent:

        available_dimensions = extract_dimension_names(
            context
        )

        requested_dimensions = intent.get(
            "group_by",
            []
        )

        invalid_dimensions = []

        for dimension in requested_dimensions:

            if dimension not in available_dimensions:

                invalid_dimensions.append(
                    dimension
                )

        if invalid_dimensions:

            raise ValueError(
                f"Invalid dimensions: "
                f"{invalid_dimensions}"
            )

        return intent