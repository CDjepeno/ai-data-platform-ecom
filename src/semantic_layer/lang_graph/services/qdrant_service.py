from json import load

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)
from config_env import settings

from utils.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

class QdrantServiceError(Exception):
    """Domain-specific exception for QdrantService failures."""


class QdrantService:

    def __init__(
        self,
        host: str,
        port: int,
        collection_name: str,
        qdrant_client: QdrantClient,
        size: int
    ):

        self._collection_name = collection_name
        self._host = host
        self._port = port
        self._client = qdrant_client
        self._size = size

    def create_collection(self) -> None:
        """Create the collection if it does not already exist."""
        existing = self._get_existing_collection_names()

        if self._collection_name in existing:
            logger.info("ℹ️ Collection already exists: %s", self._collection_name)
            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(
                size=self._size,
                distance=Distance.COSINE,
            ),
        )
        logger.info("✅ Collection created: %s", self._collection_name)

    def insert_embedding(
        self,
        point_id: str,
        embedding: list[float],
        payload: dict,
    ):

        self._client.upsert(
            collection_name=self._collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            ],
        )

        logger.info(f"✅ Inserted embedding id={point_id}")

    def search(
        self,
        embedding: list[float],
        limit: int = 3,
    ):

        results = self._client.query_points(  # type: ignore
            collection_name=self._collection_name,
            query=embedding,
            limit=limit,
        )

        return results

    def recreate_collection(self) -> None:
        
        collections = self._client.get_collections()
        existing = [c.name for c in collections.collections]

        if self._collection_name in existing:
            self._client.delete_collection(self._collection_name)
            logger.info(f"🗑️ Collection dropped: {self._collection_name}")

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(
                size=settings.qdrant_size,
                distance=Distance.COSINE,
            ),
        )
        logger.info(f"✅ Collection recreated: {self._collection_name}")
    
    
    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_existing_collection_names(self) -> list[str]:
        collections = self._client.get_collections()
        return [c.name for c in collections.collections]

    def _assert_collection_exists(self) -> None:
        """Raise early with a clear message instead of letting Qdrant 404."""
        if self._collection_name not in self._get_existing_collection_names():
            raise QdrantServiceError(
                f"Collection '{self._collection_name}' does not exist in Qdrant. "
                "Run the ETL pipeline to recreate it."
            )

    def _validate_embedding(self, embedding: list[float]) -> None:
        """
        Validate that the embedding is non-empty and has the expected dimension.
        Catches the most common silent corruption bug.
        """
        if not embedding:
            raise QdrantServiceError("Embedding vector is empty — cannot insert or search.")

        if len(embedding) != self._size:
            raise QdrantServiceError(
                f"Embedding dimension mismatch: expected {self._size}, got {len(embedding)}."
            )