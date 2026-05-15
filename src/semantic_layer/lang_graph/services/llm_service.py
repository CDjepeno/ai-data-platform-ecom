import json
from typing import AsyncIterator, Optional, TypeAlias, cast

from lang_graph.services.http_service import HttpxClient
from lang_graph.typing.llm.request_type import DeepSeekRequest
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

        payload: DeepSeekRequest = {
            "model": model_to_use,
            "messages": [{"role": "user", "content": prompt}],
        }

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        logger.info(f"🌐 Calling LLM API: {self._base_url}")

        logger.info(f"🧠 Payload: {payload}")

        response = await self._http_client.post(
            f"{self._base_url}/chat/completions",
            body=json.dumps(payload),
            headers=headers,
        )

        if response["status_code"] >= 400:
            return "LLM error: HTTP failure"

        if self._debug:
            print(f"DEBUG MODEL USED: {model_to_use}")
            print("DEBUG RAW RESPONSE:", response["text"])

        data: DeepSeekResponse = json.loads(response["text"])

        if not data["choices"]:
            return "LLM error: empty response"

        return data["choices"][0]["message"]["content"]

    JSONPrimitive: TypeAlias = str | int | float | bool | None
    JSONValue: TypeAlias = JSONPrimitive | dict[str, "JSONValue"] | list["JSONValue"]
    JSONObject: TypeAlias = dict[str, JSONValue]

    async def stream(
        self,
        prompt: str,
        use_coder: bool = False,
    ) -> AsyncIterator[str]:

        model_to_use = self._coder_model if use_coder else self._model

        payload: dict[str, object] = {
            "model": model_to_use,
            "messages": [{"role": "user", "content": prompt}],
            "stream": True,
        }

        headers: dict[str, str] = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        async for line in self._http_client.stream(
            f"{self._base_url}/chat/completions",
            headers=headers,
            json_body=payload,
        ):

            if not line:
                continue

            if not line.startswith("data: "):
                continue

            raw = line[len("data: ") :]

            if raw == "[DONE]":
                break

            chunk_raw = json.loads(raw)
            if not isinstance(chunk_raw, dict):
                continue

            chunk: dict[str, object] = cast(dict[str, object], chunk_raw)

            choices_raw = chunk.get("choices")

            if not isinstance(choices_raw, list) or not choices_raw:
                continue

            choices = cast(list[object], choices_raw)

            first_choice_raw = choices[0]

            if not isinstance(first_choice_raw, dict):
                continue

            first_choice = cast(dict[str, object], first_choice_raw)

            delta_raw = first_choice.get("delta")

            if not isinstance(delta_raw, dict):
                continue

            delta = cast(dict[str, object], delta_raw)

            content = delta.get("content")

            if isinstance(content, str):
                yield content
