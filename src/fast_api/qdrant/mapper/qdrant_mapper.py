from qdrant_client.http.models import QueryResponse


class QdrantMapper:

    @staticmethod
    def to_semantic_context(
        response: QueryResponse,
    ) -> dict:

        semantic_context = {
            "metrics": [],
            "models": [],
            "dimensions": [],
        }

        for point in response.points:

            payload = point.payload
            
            if not payload:
                continue

            payload_type = payload.get(
                "type"
            )

            if payload_type == "metric":

                semantic_context["metrics"].append(
                    payload
                )

            elif payload_type == "semantic_model":

                semantic_context["models"].append(
                    payload
                )

        return semantic_context