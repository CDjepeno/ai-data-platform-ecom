from typing import TypedDict





class SemanticDimension(TypedDict):

    name: str

    type: str

class SemanticModel(TypedDict):

    name: str

    description: str


class SemanticMetric(TypedDict):

    metric_name: str

    metric_type: str

    content: str

class SemanticContext(TypedDict):

    metrics: list[SemanticMetric]

    dimensions: list[SemanticDimension]

    semantic_models: list[SemanticModel]
    
    
class AnalyticsIntent(TypedDict):

    metrics: list[str]

    group_by: list[str]

    filters: list[str]
    

class AnalyticsState(TypedDict,total=False,):

    question: str

    semantic_context: SemanticContext

    intent: AnalyticsIntent

    metricflow_query: list[str]

    results: list

    response: str
    


