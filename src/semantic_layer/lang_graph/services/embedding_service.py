from utils.logger import get_logger


logger = get_logger(__name__)



import asyncio
from typing import Sequence, List
from sentence_transformers import SentenceTransformer



class BGEFrEnEmbedderAdapter():

    def __init__(
        self,
        model_name: str,
        device: str = "cpu",
    ):
        self._model = SentenceTransformer(
            model_name,
            device=device,
            local_files_only=True,
        )

        # ❌ NO .half() ON CPU
        self._dimension = 384

    async def embed(self, text: str) -> List[float]:

        if not text or not text.strip():
            return []

        embedding = await asyncio.to_thread(
            self._model.encode,
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    async def embed_batch(
        self,
        texts: Sequence[str],
    ) -> Sequence[Sequence[float]]:

        if not texts:
            return []

        valid_texts = [t for t in texts if t and t.strip()]

        if not valid_texts:
            return [[] for _ in texts]

        print(f"🧠 Embedding batch: {len(valid_texts)} texts")

        embeddings = await asyncio.to_thread(
            self._model.encode,
            valid_texts,
            normalize_embeddings=True,
            show_progress_bar=False,
            batch_size=8,
        )

        result = []

        idx = 0

        for t in texts:
            if t and t.strip():
                result.append(embeddings[idx].tolist())
                idx += 1
            else:
                result.append([])

        return result

    @property
    def dimension(self) -> int:
        return self._dimension
