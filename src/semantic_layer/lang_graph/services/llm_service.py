import json
from typing import AsyncIterator, Optional

from lang_graph.services.http_service import HttpxClient
from lang_graph.typing.llm.response_type import DeepSeekResponse
from utils.logger import get_logger

logger = get_logger(__name__)


class LlmService:
    def __init__(
        self,
        http_client: HttpxClient,
        api_key: str,
        base_url: str,
        model: str,  # default model
        coder_model: Optional[str] = None,  # model specialized for code
        debug: bool = False,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url
        self._model = model
        self._coder_model = coder_model or model  # fallback to default model
        self._debug = debug
        self._http_client = http_client

    async def generate(self, prompt: str, use_coder: bool = False) -> str:
        model_to_use = self._coder_model if use_coder else self._model

        payload = {
            "model": model_to_use,
            "messages": [{"role": "user", "content": prompt}],
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        response = await self._http_client.post(
            f"{self._base_url}/chat/completions",
            json_body=payload,
            headers=headers,
        )

        if response["status_code"] >= 400:
            return "LLM error: HTTP failure"

        if self._debug:
            pass

        data: DeepSeekResponse = json.loads(response["text"])

        if not data["choices"]:
            return "LLM error: empty response"

        return data["choices"][0]["message"]["content"]



    async def stream(self, prompt: str, use_coder: bool = False) -> AsyncIterator[str]:
        model_to_use = self._coder_model if use_coder else self._model
        payload = {
            "model": model_to_use,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        buffer = ""
        async for chunk in self._http_client.stream(
            f"{self._base_url}/chat/completions",
            headers=headers,
            json_body=payload,
        ):
            buffer += chunk
            # Découpage par lignes complètes
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                line = line.strip()
                if not line:
                    continue
                if line.startswith(":"):
                    continue
                if not line.startswith("data: "):
                    continue
                raw = line[len("data: "):].strip()
                if not raw or raw == "[DONE]":
                    if raw == "[DONE]":
                        return
                    continue
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    # Passe en debug pour éviter les warnings intempestifs
                    logger.debug(f"Failed to parse JSON chunk: {raw}")
                    continue
                delta = data.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content")
                if content:
                    yield content