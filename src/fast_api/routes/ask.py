

from core.http_client import client

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()


class AskRequest(BaseModel):
    question: str

@router.post("/ask")
async def ask_question(payload: AskRequest):
    async def generate():
        async with client.stream(
            "POST",
            "http://semantic_layer:8001/ask",
            json={"question": payload.question},
            headers={"Content-Type": "application/json"},
            timeout=None,  # important to avoid long timeouts
        ) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes():
                yield chunk
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )