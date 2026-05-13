from openai import AsyncOpenAI
from sqlalchemy import Sequence

from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIEmbedderService():

    def __init__(
        self,
        client: AsyncOpenAI,
        model: str = "text-embedding-3-small",
    ) -> None:
        self._client = client
        self._model = model

    async def embed(
        self,
        text: str,
    ) -> list[float]:

        if not text.strip():
            logger.warning(
                "⚠️ Empty text received for embedding"
            )
            return []

        try:
            response = await self._client.embeddings.create(
                model=self._model,
                input=text,
            )

            return response.data[0].embedding

        except Exception as e:
            logger.exception(
                f"❌ Embedding generation failed: {e}"
            )
            return []
        
    
    async def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:

        if not texts:
            return []

        try:

            response = await self._client.embeddings.create(
                model=self._model,
                input=texts,
            )

            return [
                item.embedding
                for item in response.data
            ]

        except Exception as e:

            logger.exception(
                f"❌ Batch embedding failed: {e}"
            )

            return []


    