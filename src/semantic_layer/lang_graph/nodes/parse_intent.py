import json

from dotenv import load_dotenv

from lang_graph.prompts.analytics_prompt import build_analytics_prompt
from lang_graph.typing.analytics_state import AnalyticsState
from lang_graph.utils.timer import async_timed_node
from lang_graph.utils.date_resolver import resolve_relative_period
from utils.logger import get_logger
from lang_graph.factory.factory_service import get_llm_service

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

    raw_intent = await get_llm_service().generate(prompt)

    intent = json.loads(raw_intent)
    
    relative_period = intent.get("relative_period")
    n_days = intent.get("n_days")

    if relative_period:
        start_time, end_time = resolve_relative_period(relative_period, n_days)
        intent["start_time"] = start_time
        intent["end_time"] = end_time
        intent["relative_period"] = None  # nettoie
        intent["n_days"] = None

    logger.info(f"🎯 Intent parsed: {intent}")

    return {"intent": intent}
