from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from lang_graph.graphs.analytics_graph import analytics_graph
from lang_graph.factory.factory_service import llm_service

router = APIRouter()


class AskRequest(BaseModel):
    question: str


@router.post("/ask")
async def ask_question(payload: AskRequest):

    result = await analytics_graph.ainvoke(
        {
            "question": payload.question
        }
    )

    prompt = result["final_prompt"]

    async def generate():

        async for chunk in llm_service.stream(prompt):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="text/plain"
    )