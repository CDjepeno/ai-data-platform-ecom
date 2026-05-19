from typing import Literal, TypedDict





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

class Period(TypedDict):
    start_time: str
    end_time: str
    
    
class AnalyticsIntent(TypedDict):

    metrics: list[str]

    group_by: list[str]

    filters: list[str]
    start_time: str | None   
    end_time: str | None     
    where: str | None 
    query_type: str          
    period_1: Period | None  
    period_2: Period | None
    

class PeriodResult(TypedDict):
    range: Period
    data: str


class SimpleResult(TypedDict):
    query_type: Literal["simple"]
    stdout: str
    stderr: str
    returncode: int


class ComparisonResult(TypedDict):
    query_type: Literal["comparison"]
    period_1: PeriodResult
    period_2: PeriodResult

class AnalyticsState(TypedDict,total=False,):

    question: str

    semantic_context: SemanticContext

    intent: AnalyticsIntent

    metricflow_query: list[str]

    response: str
    
    final_prompt: str
    
    results: SimpleResult | ComparisonResult
    


