from multiprocessing.util import get_logger
from time import perf_counter

import httpx

from etl_ecom.application.ports.secondary.semantic_layer_port import SemanticLayerPort
logger = get_logger(__name__)



class HttpSemanticLayerAdapter(SemanticLayerPort):
    def __init__(self, base_url: str):
        self._base_url = base_url

    def build_dbt(self) -> None:
        with httpx.Client(timeout=300) as client:
            start = perf_counter()
            client.post(f"{self._base_url}/build-dbt").raise_for_status()
            duration = perf_counter() - start
            logger.info(
                "dbt build completed in %.2f seconds",
                duration,
            )

    def index(self) -> None:
        with httpx.Client(timeout=300) as client:
            start = perf_counter()
            client.post(f"{self._base_url}/index").raise_for_status()
            duration = perf_counter() - start
            logger.info(
                "indexing completed in %.2f seconds",
                duration,
            )
