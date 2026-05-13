import uuid
import yaml

from pathlib import Path

from lang_graph.services.embedding_service import (
    OpenAIEmbedderService,
)

from lang_graph.services.qdrant_service import (
    QdrantService,
)

from etl_ecom.utils.logger import (
    get_logger,
)

logger = get_logger(__name__)


class MetricIndexer:

    def __init__(
        self,
        embedder: OpenAIEmbedderService,
        qdrant: QdrantService,
    ):

        self._embedder = embedder

        self._qdrant = qdrant

    async def index_metrics(self):

        metrics_path = Path(
            "src/etl_ecom/semantic_layer/metrics"
        )

        for file in metrics_path.glob("*.yml"):

            logger.info(
                f"📄 Indexing metrics from {file.name}"
            )

            with open(file, "r") as f:

                data = yaml.safe_load(f)

            metrics = data.get(
                "metrics",
                [],
            )

            for metric in metrics:

                text_to_embed = (
                    self._build_metric_text(
                        metric
                    )
                )

                embedding = await (
                    self._embedder.embed(
                        text_to_embed
                    )
                )

                payload = {

                    "type": "metric",

                    "metric_name": metric.get(
                        "name"
                    ),

                    "metric_type": metric.get(
                        "type"
                    ),

                    "content": text_to_embed,
                }

                self._qdrant.insert_embedding(

                    point_id=str(uuid.uuid4()),

                    embedding=embedding,

                    payload=payload,
                )

                logger.info(
                    f"✅ Indexed metric "
                    f"{metric.get('name')}"
                )

    def _build_metric_text(
        self,
        metric: dict,
    ) -> str:

        lines = []

        lines.append(
            f"Metric: "
            f"{metric.get('name')}"
        )

        lines.append(
            f"Description: "
            f"{metric.get('description', '')}"
        )

        lines.append(
            f"Type: "
            f"{metric.get('type', '')}"
        )

        lines.append(
            f"Label: "
            f"{metric.get('label', '')}"
        )

        type_params = metric.get(
            "type_params",
            {},
        )

        lines.append(
            f"Measure: "
            f"{type_params.get('measure', '')}"
        )

        return "\n".join(lines)