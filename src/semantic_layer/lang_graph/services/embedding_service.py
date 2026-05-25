import asyncio
import logging
from functools import lru_cache
from typing import Final, Protocol, Sequence, runtime_checkable

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)



@runtime_checkable
class EmbedderPort(Protocol):
    """Port interface for text embedding adapters."""

    async def embed(self, text: str) -> list[float]:
        """Embed a single text. Returns empty list for blank input."""
        ...

    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed a batch of texts. Preserves order, empty string → empty list."""
        ...

    @property
    def dimension(self) -> int:
        """Return the embedding vector dimension."""
        ...



class BGEFrEnEmbedderAdapter:

    def __init__(
        self,
        model_name: str,
        device: str = "cpu",
    ) -> None:
        logger.info("Loading embedding model '%s' on device '%s'", model_name, device)

        self._model = SentenceTransformer(
            model_name,
            device=device,
            local_files_only=False,
        )

        # Read dimension directly from the model — never hardcode
        raw_dimension = self._model.get_embedding_dimension()

        if raw_dimension is None:
            raise ValueError(
                f"Model '{model_name}' returned None for embedding dimension — "
                "the model may be corrupted or incompatible."
            )

        self._dimension: int = raw_dimension

        logger.info(
            "Embedding model loaded — dimension=%d device=%s",
            self._dimension,
            device,
        )

    async def embed(self, text: str) -> list[float]:

        if not text or not text.strip():
            logger.debug("embed() received blank text — returning empty list")
            return []

        try:
            embedding = await asyncio.to_thread(
                self._model.encode,
                text,
                normalize_embeddings=True,
            )
            return embedding.tolist()

        except Exception as exc:
            logger.exception("Failed to embed text: %s", exc)
            raise EmbeddingError(f"Embedding failed for input: {text!r}") from exc

    async def embed_batch(self, texts: Sequence[str]) -> list[list[float]]:

        if not texts:
            return []

        # Separate valid texts and track their original positions
        indexed_valid: list[tuple[int, str]] = [
            (i, t) for i, t in enumerate(texts) if t and t.strip()
        ]

        if not indexed_valid:
            return [[] for _ in texts]

        valid_texts = [t for _, t in indexed_valid]

        logger.debug("Embedding batch of %d valid texts (total=%d)", len(valid_texts), len(texts))

        try:
            embeddings = await asyncio.to_thread(
                self._model.encode,
                valid_texts,
                normalize_embeddings=True,
                show_progress_bar=False,
                batch_size=8,
            )
        except Exception as exc:
            logger.exception("Failed to embed batch: %s", exc)
            raise EmbeddingError(f"Batch embedding failed for {len(valid_texts)} texts") from exc

        # Reconstruct the full result list preserving original positions
        result: list[list[float]] = [[] for _ in texts]
        for embed_idx, (original_idx, _) in enumerate(indexed_valid):
            result[original_idx] = embeddings[embed_idx].tolist()

        return result

    @property
    def dimension(self) -> int:
        return self._dimension



class EmbeddingError(Exception):
    """Raised when the embedding model fails to process input."""



MODEL_NAME: Final[str] = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

@lru_cache(maxsize=1)
def get_embedder() -> BGEFrEnEmbedderAdapter:

    return BGEFrEnEmbedderAdapter(model_name=MODEL_NAME, device="cpu")