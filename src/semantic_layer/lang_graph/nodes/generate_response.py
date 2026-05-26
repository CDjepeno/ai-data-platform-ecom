from collections.abc import AsyncIterator
from typing import Any

from dotenv import load_dotenv

from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.factory.factory_service import get_llm_service
from lang_graph.utils.timer import async_timed_node

load_dotenv()


@async_timed_node(
    "generate_response"
)
async def generate_response(state: AnalyticsState, *args, **kwargs):
    writer = kwargs.get('writer')
    if writer is None and len(args) > 0:
        writer = args[0]  # safety fallback
    print(f"DEBUG: writer = {writer}")  # important

    prompt = state.get("final_prompt")
    if not prompt:
        raise ValueError("Final prompt missing from state")

    async for chunk in get_llm_service().stream(prompt):
        if chunk:
            if writer:
                writer(chunk)   # immediate send
            yield {"response": chunk}  # for state (not used in custom mode)