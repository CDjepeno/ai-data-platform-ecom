
from lang_graph.factory.factory_service import qdrant_service
from lang_graph.factory.factory_service import embedding_service
from lang_graph.typing.analytics_state import AnalyticsState
from qdrant.mapper.qdrant_mapper import QdrantMapper


async def retrieve_context(state: AnalyticsState):

    question = state.get("question")
    
    if not question:

        raise ValueError(
            "Question missing from state"
        ) 

    
    embedding = await embedding_service.embed(question)
    
  
    context = qdrant_service.search(embedding)
    
    results = QdrantMapper.to_semantic_context(
        context
    )

    return {
        "semantic_context": results
    }