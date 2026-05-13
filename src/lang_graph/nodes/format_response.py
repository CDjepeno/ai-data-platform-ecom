from dotenv import load_dotenv

from etl_ecom.db.db_config import Config



from lang_graph.nodes.build_format_response import build_formatting_prompt
from lang_graph.services.http_service import (
    HttpxClient,
)

from lang_graph.services.llm_service import (
    LlmService,
)

from lang_graph.typing.analytics_state import (
    AnalyticsState,
)

load_dotenv()


async def format_response(
    state: AnalyticsState,
):

    question = state.get("question")

    results = state.get("results")  
    
    if not question:

        raise ValueError(
            "Question missing from state"
        )


    if not results:

        raise ValueError(
            "Results missing from state"
        )

    prompt = build_formatting_prompt(
        question=question,
        results=results,
    )

    http_client = HttpxClient()

    api_key = Config.DEEP_SEEK_API

    base_url = Config.BASE_URL_DEEP_SEEK_API

    if not api_key or not base_url:

        raise ValueError(
            "LLM configuration missing"
        )

    model = Config.MODEL_DEEP_SEEK

    llm = LlmService(
        http_client=http_client,
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    response = await llm.generate(
        prompt
    )

    return {
        "response": response
    }