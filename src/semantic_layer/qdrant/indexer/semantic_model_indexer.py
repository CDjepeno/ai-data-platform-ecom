import uuid
import yaml

from pathlib import Path

from config_env import Config
from utils.logger import get_logger
from lang_graph.services.embedding_service import BGEFrEnEmbedderAdapter
from lang_graph.services.qdrant_service import QdrantService


logger = get_logger(__name__)


class SemanticModelsIndexer:

    def __init__(
        self,
        embedder: BGEFrEnEmbedderAdapter,
        qdrant: QdrantService,
    ):
        self._embedder = embedder
        self._qdrant = qdrant

    async def index_semantic_models(self):

        semantic_path = Config.SEMANTIC_MODELS_PATH

        if not semantic_path.exists():
            logger.error(f"❌ Path not found: {semantic_path}")
            raise FileNotFoundError(f"Semantic models path not found: {semantic_path}")

        files = list(semantic_path.glob("*.yml"))

        if not files:
            logger.error(f"❌ No .yml files found in: {semantic_path}")
            raise ValueError(f"No .yml files found in: {semantic_path}")

        logger.info(f"📂 Found {len(files)} files to index in {semantic_path}")

        indexed = 0
        errors = []

        for file in files:
            try:
                logger.info(f"📄 Indexing {file.name}")

                with open(file, "r") as f:
                    data = yaml.safe_load(f)

                if not data:
                    logger.warning(f"⚠️ Empty or invalid YAML: {file.name}")
                    continue

                text_to_embed = self._build_semantic_text(data)

                if not text_to_embed.strip():
                    logger.warning(f"⚠️ Empty text generated for: {file.name}")
                    continue

                logger.info(f"🧠 Embedding {file.name} ({len(text_to_embed)} chars)")
                embedding = await self._embedder.embed(text_to_embed)

                if not embedding:
                    logger.error(f"❌ Empty embedding returned for: {file.name}")
                    errors.append(file.name)
                    continue

                logger.info(f"📐 Embedding dimension: {len(embedding)}")

                payload = {
                    "file_name": file.name,
                    "content": text_to_embed,
                }

                self._qdrant.insert_embedding(
                    point_id=str(uuid.uuid4()),
                    embedding=embedding,
                    payload=payload,
                )

                indexed += 1
                logger.info(f"✅ Indexed {file.name}")

            except Exception as e:
                logger.exception(f"❌ Failed to index {file.name}: {e}")
                errors.append(file.name)

        logger.info(f"📊 Indexing complete: {indexed}/{len(files)} files indexed")

        if errors:
            logger.error(f"❌ Failed files: {errors}")
            raise RuntimeError(f"Indexing failed for: {errors}")

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
