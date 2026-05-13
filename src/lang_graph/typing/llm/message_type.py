
from typing import Literal, TypedDict


class DeepSeekMessage(TypedDict):
    role: Literal[
        "system",
        "user",
        "assistant",
    ]
    content: str