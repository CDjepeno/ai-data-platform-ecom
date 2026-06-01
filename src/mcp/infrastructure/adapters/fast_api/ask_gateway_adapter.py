
from __future__ import annotations

from collections.abc import AsyncIterator

from domain.services import parse_sse_line
from domain.tools.sse import SseLine
from domain.ports.ask_gateway_port import AskGatewayPort
from infrastructure.adapters.fast_api.http_stream_reader import HttpStreamReader
from utils import get_logger


logger = get_logger(__name__)

# FastAPI /ask endpoint path — the only place this is hardcoded
_ASK_PATH = "/ask"


class FastApiAskGatewayAdapter(AskGatewayPort):

    def __init__(self, stream_reader: HttpStreamReader) -> None:
        self._reader = stream_reader

    async def stream(self, question: str) -> AsyncIterator[SseLine]:  # type: ignore[override]
        """
        Call FastAPI /ask and yield typed SseLine domain objects.

        Converts the raw string lines from HttpStreamReader into
        typed value objects using the domain parsing service.

        Args:
            question: Natural language business question.

        Yields:
            SseLine subclasses — SseEmpty, SseStep, SseToken.

        Raises:
            StreamErrorSignal: if [ERROR] appears in the stream.
            RuntimeError:      if HTTP or network error occurs.
        """
        logger.debug(
            "FastApiAskGateway.stream | question=%r",
            question[:80],
        )

        # Build the FastAPI-specific payload shape
        payload = {"question": question}

        # Delegate transport to HttpStreamReader
        # Convert raw lines to typed domain objects via domain service
        async for raw_line in self._reader.stream_lines(_ASK_PATH, payload):
            yield parse_sse_line(raw_line)