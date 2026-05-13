

import http
import json

from dotenv import load_dotenv

from etl_ecom.db.db_config import Config
from lang_graph.prompts.analytics_prompt import build_analytics_prompt
from lang_graph.services.http_service import HttpxClient
from lang_graph.services.llm_service import LlmService
from lang_graph.typing.analytics_state import AnalyticsState
from etl_ecom.utils.logger import get_logger

logger = get_logger(__name__)

load_dotenv()

async def parse_intent(state: AnalyticsState):

    
    context = state.get("semantic_context")
    
    if not context:

        raise ValueError(
            "Semantic context missing from state"
        )
        
    logger.debug(
        f"Semantic context retrieved: "
        f"{len(context.get('metrics', []))} metrics, "
        f"{len(context.get('dimensions', []))} dimensions"
    )

    question = state.get("question")
    
    if not question:
        raise ValueError(
            "Question missing from state"
        )

    logger.info(
        f"🧠 Parsing analytics intent for question: {question}"
    )
    
    http_client = HttpxClient()
    
    api_key = Config.DEEP_SEEK_API
    
    base_url = Config.BASE_URL_DEEP_SEEK_API
    
    if not api_key or not base_url:
        raise ValueError(
            "DEEP_SEEK_API or BASE_URL_DEEP_SEEK_API is not configured"
        )
    
    model = Config.MODEL_DEEP_SEEK
    
    logger.info(
        "🚀 Sending prompt to LLM"
    )
    
    llm = LlmService(
        http_client=http_client,
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
        model=model
    )
    
    prompt = build_analytics_prompt(
        question=question,
        context=context,
    )

    raw_intent = await llm.generate(prompt)
    
    logger.info(
        f"🧠 Raw LLM response:\n{raw_intent}"
    )
    
    intent = json.loads(raw_intent)
    
    logger.info(
        f"✅ Parsed intent: {intent}"
    )

    return {
        "intent": intent
    }