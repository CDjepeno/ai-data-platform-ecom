from fastapi import APIRouter
from pydantic import BaseModel

from lang_graph.graphs.analytics_graph import (
    analytics_graph,
)


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

    return result["response"]