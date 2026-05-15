import uuid
import yaml

from pathlib import Path

from utils.logger import get_logger
from lang_graph.services.embedding_service import OpenAIEmbedderService
from lang_graph.services.qdrant_service import QdrantService


logger = get_logger(__name__)


class SemanticModelsIndexer:

    def __init__(
        self,
        embedder: OpenAIEmbedderService,
        qdrant: QdrantService,
    ):
        self._embedder = embedder
        self._qdrant = qdrant

    async def index_semantic_models(self):

        semantic_path = Path("src/etl_ecom/transformations/mart/semantic_models")

        for file in semantic_path.glob("*.yml"):

            logger.info(f"📄 Indexing {file.name}")

            with open(file, "r") as f:
                data = yaml.safe_load(f)

            text_to_embed = self._build_semantic_text(data)

            embedding = await self._embedder.embed(text_to_embed)

            payload = {
                "file_name": file.name,
                "content": text_to_embed,
            }

            self._qdrant.insert_embedding(
                point_id=str(uuid.uuid4()),
                embedding=embedding,
                payload=payload,
            )

            logger.info(f"✅ Indexed {file.name}")

    def _build_semantic_text(self, data: dict) -> str:

        lines = []

        lines.append(f"Model: {data.get('name')}")

        lines.append(f"Description: {data.get('description', '')}")

        dimensions = data.get("dimensions", [])

        for dim in dimensions:
            lines.append(f"Dimension: {dim.get('name')} - {dim.get('description', '')}")

        measures = data.get("measures", [])

        for measure in measures:
            lines.append(
                f"Measure: {measure.get('name')} - {measure.get('description', '')}"
            )

        return "\n".join(lines)
