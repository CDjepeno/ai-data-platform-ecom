from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(payload: AskRequest):

    async def generate():

        async with httpx.AsyncClient(timeout=None) as client:

            async with client.stream(
                "POST",
                "http://semantic_layer:8001/ask",
                json={
                    "question": payload.question
                }
            ) as response:

                async for chunk in response.aiter_text():

                    yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )