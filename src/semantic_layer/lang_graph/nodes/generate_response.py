from collections.abc import AsyncIterator
from typing import Any

from dotenv import load_dotenv

from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.factory.factory_service import llm_service

load_dotenv()


async def generate_response(state: AnalyticsState, *args, **kwargs):
    writer = kwargs.get('writer')
    if writer is None and len(args) > 0:
        writer = args[0]  # sécurité
    print(f"DEBUG: writer = {writer}")  # important

    prompt = state.get("final_prompt")
    if not prompt:
        raise ValueError("Final prompt missing from state")

    async for chunk in llm_service.stream(prompt):
        if chunk:
            print(f"DEBUG: chunk received = {chunk}")  # déjà présent
            if writer:
                writer(chunk)   # envoi immédiat
            yield {"response": chunk}  # pour l'état (non utilisé en custom)