from __future__ import annotations

from typing import Literal
from pydantic import BaseModel


class MetricPayloadDTO(BaseModel):
    """
    Contract for metric payloads stored in Qdrant.
    Represents a dbt MetricFlow metric (not a measure).
    
    Example:
        metric_name: total_orders
        measure_ref: order_count  ← the underlying measure
    """

    type: Literal["metric"] = "metric"
    file_name: str
    metric_name: str
    description: str = ""
    label: str = ""
    measure_ref: str = ""

    model_config = {"frozen": True}

    def to_embedding_text(self) -> str:
        """Text used for vector embedding — single source of truth."""
        return "\n".join([
            f"Metric: {self.metric_name}",
            f"Label: {self.label}",
            f"Description: {self.description}",
            f"Measure: {self.measure_ref}",
        ])

    @classmethod
    def from_yaml(cls, file_name: str, data: dict) -> list[MetricPayloadDTO]:
        """Builds a list of DTOs from a parsed dbt metrics YAML file."""
        return [
            cls(
                file_name=file_name,
                metric_name=m.get("name", ""),
                description=m.get("description", ""),
                label=m.get("label", ""),
                measure_ref=m.get("type_params", {}).get("measure", ""),
            )
            for m in data.get("metrics", [])
        ]