# lang_graph/services/embedding_service.py

from __future__ import annotations

import logging
from typing import Final, Protocol, Sequence, runtime_checkable

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


@runtime_checkable
class EmbedderPort(Protocol):
    """Port interface for text embedding adapters."""

    async def embed(self, text: str) -> list[float]: ...
    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]: ...

    @property
    def dimension(self) -> int: ...


class EmbeddingError(Exception):
    """Raised when the embedding model fails to process input."""


# OpenAI model → output dimension mapping
# https://platform.openai.com/docs/models/embeddings
_OPENAI_DIMENSIONS: Final[dict[str, int]] = {
    "text-embedding-3-small": 1536,
    "text-embedding-3-large": 3072,
    "text-embedding-ada-002": 1536,
}


class OpenAIEmbedderAdapter:
    """
    Adapter wrapping OpenAI embeddings API.
    No local model — pure HTTP call to OpenAI.
    Drop-in replacement for BGEFrEnEmbedderAdapter via EmbedderPort protocol.
    """

    def __init__(
        self,
        model_name: str,
        api_key: str,
    ) -> None:
        if model_name not in _OPENAI_DIMENSIONS:
            raise ValueError(
                f"Unknown OpenAI embedding model '{model_name}'. "
                f"Known models: {list(_OPENAI_DIMENSIONS.keys())}"
            )

        self._model_name = model_name
        self._dimension: Final[int] = _OPENAI_DIMENSIONS[model_name]
        self._client = AsyncOpenAI(api_key=api_key)

        logger.info(
            "OpenAIEmbedderAdapter ready — model=%s dimension=%d",
            self._model_name,
            self._dimension,
        )

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            logger.debug("embed() received blank input — returning empty list")
            return []

        try:
            response = await self._client.embeddings.create(
                model=self._model_name,
                input=text,
            )
            return response.data[0].embedding

        except Exception as exc:
            logger.exception("embed() failed for model=%s", self._model_name)
            raise EmbeddingError(f"OpenAI embedding failed: {exc}") from exc

    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []

        indexed_valid: list[tuple[int, str]] = [
            (i, t) for i, t in enumerate(texts) if t and t.strip()
        ]
        if not indexed_valid:
            return [[] for _ in texts]

        valid_texts = [t for _, t in indexed_valid]
        logger.debug("embed_batch() valid=%d total=%d", len(valid_texts), len(texts))

        try:
            response = await self._client.embeddings.create(
                model=self._model_name,
                input=valid_texts,
            )
        except Exception as exc:
            logger.exception("embed_batch() failed for model=%s", self._model_name)
            raise EmbeddingError(
                f"OpenAI batch embedding failed for {len(valid_texts)} texts"
            ) from exc

        # Reconstruct full result list preserving original positions
        result: list[list[float]] = [[] for _ in texts]
        for embed_idx, (original_idx, _) in enumerate(indexed_valid):
            result[original_idx] = response.data[embed_idx].embedding

        return result

    @property
    def dimension(self) -> int:
        return self._dimension