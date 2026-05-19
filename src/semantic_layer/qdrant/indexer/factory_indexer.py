
from qdrant.indexer.semantic_model_indexer import SemanticModelsIndexer
from lang_graph.factory.factory_service import qdrant_service
from lang_graph.services.embedding_service import BGEFrEnEmbedderAdapter
from semantic_layer.config_env import Config



embedder = BGEFrEnEmbedderAdapter(model_name=Config.MODEL_EMBEDDING)

semantic_models_indexer = SemanticModelsIndexer(
        embedder=embedder,
        qdrant=qdrant_service,
    )