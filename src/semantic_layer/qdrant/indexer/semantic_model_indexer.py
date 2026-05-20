import uuid
import yaml
from pathlib import Path

from config_env import Config
from shared.dto.semantic_payload_dto import (
    SemanticModelPayloadDTO,
    MetricPayloadDTO,
    semantic_model_from_yaml,
    metric_from_yaml,
    semantic_model_to_embedding_text,
    metric_to_embedding_text,
)
from utils.logger import get_logger

logger = get_logger(__name__)


class SemanticModelsIndexer:

    def __init__(self, embedder, qdrant):
        self._embedder = embedder
        self._qdrant = qdrant
        self._semantic_path: Path = Config.SEMANTIC_MODELS_PATH
        self._metrics_path: Path = Config.METRICS_PATH

    async def index_semantic_models(self) -> None:
        self._validate_paths()
        
        self._qdrant.recreate_collection()

        semantic_files = list(self._semantic_path.glob("*.yml"))
        metric_files = list(self._metrics_path.glob("*.yml"))

        if not semantic_files and not metric_files:
            raise ValueError("No .yml files found to index")

        logger.info(
            f"📂 {len(semantic_files)} semantic models "
            f"+ {len(metric_files)} metric files to index"
        )

        indexed, errors = 0, []

        for file in semantic_files:
            success = await self._index_semantic_file(file)
            if success:
                indexed += 1
            else:
                errors.append(file.name)

        for file in metric_files:
            success = await self._index_metric_file(file)
            if success:
                indexed += 1
            else:
                errors.append(file.name)

        total = len(semantic_files) + len(metric_files)
        logger.info(f"📊 Indexing complete: {indexed}/{total} succeeded")

        if errors:
            raise RuntimeError(f"Indexing failed for: {errors}")

    async def _index_semantic_file(self, file: Path) -> bool:
        try:
            logger.info(f"📄 Indexing semantic model: {file.name}")
            data = self._load_yaml(file)
            payload = semantic_model_from_yaml(file.name, data)
            text = semantic_model_to_embedding_text(payload)
            logger.info(
                f"🧠 Model: {payload['model_name']} | "
                f"measures: {len(payload['measures'])} | "
                f"dimensions: {len(payload['dimensions'])}"
            )
            return await self._embed_and_insert(file.name, text, payload)
        except Exception as e:
            logger.exception(f"❌ Failed to index {file.name}: {e}")
            return False

    async def _index_metric_file(self, file: Path) -> bool:
        try:
            logger.info(f"📄 Indexing metrics: {file.name}")
            data = self._load_yaml(file)
            payloads = metric_from_yaml(file.name, data)
            for payload in payloads:
                text = metric_to_embedding_text(payload)
                logger.info(f"🎯 Metric: {payload['metric_name']}")
                success = await self._embed_and_insert(file.name, text, payload)
                if not success:
                    return False
            return True
        except Exception as e:
            logger.exception(f"❌ Failed to index {file.name}: {e}")
            return False

    async def _embed_and_insert(
        self,
        file_name: str,
        text: str,
        payload: SemanticModelPayloadDTO | MetricPayloadDTO,
    ) -> bool:
        embedding = await self._embedder.embed(text)
        if not embedding:
            logger.error(f"❌ Empty embedding for: {file_name}")
            return False
        logger.debug(f"📐 Embedding dimension: {len(embedding)}")
        self._qdrant.insert_embedding(
            point_id=str(uuid.uuid4()),
            embedding=embedding,
            payload=dict(payload),
        )
        logger.info(f"✅ Inserted: {file_name}")
        return True

    def _load_yaml(self, file: Path) -> dict:
        with open(file, "r") as f:
            data = yaml.safe_load(f)
        if not data:
            raise ValueError(f"Empty or invalid YAML: {file.name}")
        return data

    def _validate_paths(self) -> None:
        if not self._semantic_path.exists():
            raise FileNotFoundError(
                f"Semantic models path not found: {self._semantic_path}"
            )
        if not self._metrics_path.exists():
            raise FileNotFoundError(
                f"Metrics path not found: {self._metrics_path}"
            )