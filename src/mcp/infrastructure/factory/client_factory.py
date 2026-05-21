import httpx

from infrastructure.config import Settings



def create_http_client(settings: Settings) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        base_url=str(settings.fastapi_base_url),
        timeout=httpx.Timeout(settings.mcp_http_timeout),
    )