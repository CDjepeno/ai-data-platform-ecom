from typing import TypedDict





class SemanticDimension(TypedDict):

    name: str

    type: str

class SemanticModel(TypedDict):
    type: str
    file_name: str
    model_name: str
    description: str
    dbt_model_ref: str
    measures: list[dict]
    dimensions: list[dict]
    entities: list[dict]


class SemanticMetric(TypedDict):
    type: str
    file_name: str
    metric_name: str
    description: str
    label: str
    measure_ref: str


class SemanticContext(TypedDict):

    metrics: list[SemanticMetric]

    dimensions: list[SemanticDimension]

    models: list[SemanticModel]
    
    
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
    
    final_prompt: str
    


