from __future__ import annotations
from typing import TypedDict


class SemanticModelPayloadDTO(TypedDict):
    type: str
    file_name: str
    model_name: str
    description: str
    dbt_model_ref: str
    measures: list[dict]
    dimensions: list[dict]
    entities: list[dict]


class MetricPayloadDTO(TypedDict):
    type: str
    file_name: str
    metric_name: str
    description: str
    label: str
    measure_ref: str


def semantic_model_to_embedding_text(payload: SemanticModelPayloadDTO) -> str:
    lines = [
        f"Model: {payload['model_name']}",
        f"Description: {payload['description']}",
    ]
    for m in payload["measures"]:
        lines.append(f"Measure: {m['name']} - {m.get('description', '')}")
    for d in payload["dimensions"]:
        lines.append(f"Dimension: {d['name']} - {d.get('description', '')}")
    for e in payload["entities"]:
        lines.append(f"Entity: {e['name']} - type: {e.get('type', '')}")
    return "\n".join(lines)


def metric_to_embedding_text(payload: MetricPayloadDTO) -> str:
    return "\n".join([
        f"Metric: {payload['metric_name']}",
        f"Label: {payload['label']}",
        f"Description: {payload['description']}",
        f"Measure: {payload['measure_ref']}",
    ])


def semantic_model_from_yaml(file_name: str, data: dict) -> SemanticModelPayloadDTO:
    models = data.get("semantic_models", [])
    if not models:
        raise ValueError(f"No semantic_models found in {file_name}")
    model = models[0]
    return SemanticModelPayloadDTO(
        type="semantic_model",
        file_name=file_name,
        model_name=model.get("name", ""),
        description=model.get("description", ""),
        dbt_model_ref=str(model.get("model", "")),
        measures=model.get("measures", []),
        dimensions=model.get("dimensions", []),
        entities=model.get("entities", []),
    )


def metric_from_yaml(file_name: str, data: dict) -> list[MetricPayloadDTO]:
    return [
        MetricPayloadDTO(
            type="metric",
            file_name=file_name,
            metric_name=m.get("name", ""),
            description=m.get("description", ""),
            label=m.get("label", ""),
            measure_ref=m.get("type_params", {}).get("measure", ""),
        )
        for m in data.get("metrics", [])
    ]