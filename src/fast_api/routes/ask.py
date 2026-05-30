

import time as time_module

from prometheus_client import Histogram

from core.http_client import client

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

ask_total_duration = Histogram(
    "ask_total_request_duration_seconds",
    "Total request duration including LLM streaming (graph + stream)",
)

class AskRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(payload: AskRequest):

    start = time_module.time()

    async def generate():
        async with client.stream(
            "POST",
            "http://semantic-layer:8001/ask",
            json={"question": payload.question},
            headers={"Content-Type": "application/json"},
            timeout=None,
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                yield chunk

        ask_total_duration.observe(time_module.time() - start)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )