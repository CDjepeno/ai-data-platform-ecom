import json

from dotenv import load_dotenv

from lang_graph.prompts.analytics_prompt import build_analytics_prompt
from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.utils.timer import async_timed_node
from utils.logger import get_logger
from lang_graph.factory.factory_service import llm_service

logger = get_logger(__name__)

load_dotenv()


@async_timed_node(
    "parse_intent"
)
async def parse_intent(state: AnalyticsState):

    context = state.get("semantic_context")

    if not context:

        raise ValueError("Semantic context missing from state")


    question = state.get("question")

    if not question:
        raise ValueError("Question missing from state")

    logger.info(f"🧠 Parsing analytics intent for question: {question}")

    logger.info("🚀 Sending prompt to LLM")

    prompt = build_analytics_prompt(
        question=question,
        context=context,
    )

    raw_intent = await llm_service.generate(prompt)

    intent = json.loads(raw_intent)
    logger.info(f"🎯 Intent parsed: {intent}")

    return {"intent": intent}
