from typing import cast

from qdrant_client.http.models import QueryResponse

from utils.logger import get_logger
from lang_graph.typing.analytics_state import SemanticContext, SemanticMetric, SemanticModel

logger = get_logger(__name__)


class QdrantMapper:

    @staticmethod
    def to_semantic_context(response: QueryResponse) -> SemanticContext:

        semantic_context = SemanticContext(
            metrics=[],
            models=[],
            dimensions=[],
        )
        
        seen_metrics: set[str] = set()

        for point in response.points:

            payload = point.payload

            if not payload:
                continue

            payload_type = payload.get("type")

            if payload_type == "metric":
                metric_name = payload.get("metric_name", "")
                if metric_name not in seen_metrics:  # ← déduplique
                    seen_metrics.add(metric_name)
                    semantic_context["metrics"].append(
                        cast(SemanticMetric, payload)
                )

            elif payload_type == "semantic_model":
                semantic_context["models"].append(
                    cast(SemanticModel, payload)  # ← we know this is a SemanticModel
                )

            else:
                logger.warning(f"⚠️ Unknown payload type: {payload_type}")

        return semantic_context