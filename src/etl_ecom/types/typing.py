from typing import TypedDict


class LayersConfig(TypedDict):
    bronze: str
    silver: str
    gold: str


class IncrementalConfig(TypedDict, total=False):
    enabled: bool
    watermark_column: str
    watermark_id: str


class TableConfig(TypedDict):
    source: str
    layers: LayersConfig
    primary_key: str | list[str]
    incremental: IncrementalConfig


class IngestionConfig(TypedDict):
    tables: dict[str, TableConfig]