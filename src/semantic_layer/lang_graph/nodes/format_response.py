from dotenv import load_dotenv

from lang_graph.nodes.build_format_response import (
    build_formatting_prompt,
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
        raise ValueError("Question missing from state")

    if not results:
        raise ValueError("Results missing from state")

    prompt = build_formatting_prompt(
        question=question,
        results=results,
    )

    return {
        "final_prompt": prompt
    }