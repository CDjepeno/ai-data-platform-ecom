
from typing import TypedDict

from lang_graph.typing.llm.message_type import DeepSeekMessage


class DeepSeekRequest(TypedDict, total=False):
    model: str
    messages: list[DeepSeekMessage]
    temperature: float
    stream: bool
    max_tokens: int