import time

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from lang_graph.factory.factory_service import llm_service
from lang_graph.graphs.analytics_graph import analytics_graph
from utils.logger import get_logger

router = APIRouter()

logger = get_logger(__name__)


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask(payload: AskRequest):

    request_start = time.perf_counter()

    async def generate():

        try:

            # STEP 1
            yield (
                "data: [STEP] "
                "🧠 Understanding your request...\n\n"
            )

            graph_start = time.perf_counter()

            result = await analytics_graph.ainvoke(
                {
                    "question": payload.question
                }
            )

            graph_duration = (
            time.perf_counter()
                - graph_start
            )

            logger.info(
                f"📊 GRAPH EXECUTION: "
                f"{graph_duration:.2f}s"
            )

            # STEP 2
            yield (
                "data: [STEP] "
                "📊 Query completed, generating insights...\n\n"
            )

            prompt = result.get(
                "final_prompt"
            )

            if not prompt:
                raise ValueError(
                    "final_prompt missing"
                )

            llm_start = time.perf_counter()

            async for chunk in llm_service.stream(
                prompt
            ):

                if not chunk:
                    continue

                token = str(chunk)

                yield (
                    f"data: {token}\n\n"
                )

            llm_duration = (
                time.perf_counter()
                - llm_start
            )

            total_duration = (
                time.perf_counter()
                - request_start
            )

            logger.info(
                f"🤖 LLM STREAM: "
                f"{llm_duration:.2f}s"
            )

            logger.info(
                f"🚀 TOTAL REQUEST TIME: "
                f"{total_duration:.2f}s"
            )

            # STEP 3
            yield (
                "data: [STEP] "
                "✅ Response completed\n\n"
            )

        except Exception as e:

            logger.error(
                f"Streaming error: {e}"
            )

            yield (
                f"data: [ERROR] "
                f"{str(e)}\n\n"
            )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":
                "no-cache",
            "Connection":
                "keep-alive",
            "X-Accel-Buffering":
                "no",
        },
    )