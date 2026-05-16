import json
from venv import logger

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from utils.logger import get_logger
from lang_graph.graphs.analytics_graph import analytics_graph

router = APIRouter()

logger = get_logger(__name__)
class AskRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask(payload: AskRequest):
    async def generate():
        try:
            async for event in analytics_graph.astream_events(
                {"question": payload.question},
                version="v2",
                config={"configurable": {"thread_id": "1"}},
            ):
                if event["event"] == "on_chain_stream":
                    chunk_value = event["data"].get("chunk")
                    if isinstance(chunk_value, dict) and "response" in chunk_value:
                        token = chunk_value["response"]
                        if token:
                            yield f"data: {token}\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: [ERROR] {str(e)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )