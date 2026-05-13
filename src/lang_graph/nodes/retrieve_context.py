from openai import AsyncOpenAI
from torch import embedding

from fast_api.qdrant.mapper.qdrant_mapper import QdrantMapper
from lang_graph.services.embedding_service import OpenAIEmbedderService
from lang_graph.services.qdrant_service import QdrantService
from lang_graph.typing.analytics_state import AnalyticsState


async def retrieve_context(state: AnalyticsState):

    question = state.get("question")
    
    if not question:

        raise ValueError(
            "Question missing from state"
        ) 

    
    client = AsyncOpenAI()
    
    embedder = OpenAIEmbedderService(client)
    
    embedding = await embedder.embed(question)
 
    qdrant = QdrantService()
       
    context = qdrant.search(embedding)
    
    results = QdrantMapper.to_semantic_context(
        context
    )

    return {
        "semantic_context": results
    }