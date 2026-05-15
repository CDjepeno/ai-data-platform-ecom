from json import load

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
)

from config_env import Config
from utils.logger import get_logger

logger = get_logger(__name__)

load_dotenv()


class QdrantService:

    def __init__(
        self,
        host: str,
        port: int,
        collection_name: str,
    ):

        self._collection_name = collection_name
        self._host = Config.QDRANT_HOST
        self._port = Config.QDRANT_PORT
        self._collection_name = Config.QDRANT_COLLECTION
        self._client = QdrantClient(
            host=host,
            port=port,
        )

    def create_collection(self):

        collections = self._client.get_collections()

        existing = [c.name for c in collections.collections]

        if self._collection_name in existing:

            logger.info(f"ℹ️ Collection already exists: {self._collection_name}")

            return

        self._client.create_collection(
            collection_name=self._collection_name,
            vectors_config=VectorParams(
                size=1536,
                distance=Distance.COSINE,
            ),
        )

        logger.info(f"✅ Collection created: {self._collection_name}")

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
