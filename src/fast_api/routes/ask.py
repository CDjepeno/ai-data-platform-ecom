

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
            timeout=None,  # important pour éviter les timeouts longs
        ) as response:
            response.raise_for_status()
            # Lecture ligne par ligne pour éviter le buffering
            buffer = ""
            async for chunk in response.aiter_bytes():
                buffer += chunk.decode("utf-8")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        yield line + "\n"
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )