

from typing import TypedDict

from lang_graph.typing.llm.message_type import DeepSeekMessage


class DeepSeekChoice(TypedDict):
    message: DeepSeekMessage
    finish_reason: str


class DeepSeekUsage(TypedDict):

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int


class DeepSeekResponse(TypedDict):
    choices: list[DeepSeekChoice]
    usage: DeepSeekUsage