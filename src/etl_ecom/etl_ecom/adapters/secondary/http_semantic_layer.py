import httpx

from etl_ecom.application.ports.secondary.semantic_layer_port import SemanticLayerPort


class HttpSemanticLayer(SemanticLayerPort):
    def __init__(self, base_url: str):
        self._base_url = base_url

    def build_dbt(self) -> None:
        with httpx.Client(timeout=300) as client:
            client.post(f"{self._base_url}/build-dbt").raise_for_status()

    def index(self) -> None:
        with httpx.Client(timeout=300) as client:
            client.post(f"{self._base_url}/index").raise_for_status()
