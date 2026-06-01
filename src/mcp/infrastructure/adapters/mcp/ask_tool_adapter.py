from __future__ import annotations

from mcp.types import CallToolResult, Tool

from pydantic import Field

from domain.errors import EmptyStreamError, StreamError
from application.use_cases.ask_question_usecase import AskQuestionUseCase
from domain.tools.base import AbstractTool, ToolInput, error_result, success_result
from infrastructure.adapters.fast_api.ask_gateway_adapter import FastApiAskGatewayAdapter
from infrastructure.adapters.fast_api.http_stream_reader import HttpStreamReader
from infrastructure.adapters.slack.silent_step_callback import SilentStepCallbackAdapter
from utils import get_logger

logger = get_logger(__name__)


# ── Input schema ───────────────────────────────────────────────────────────────

class AskToolInput(ToolInput):
    """Validated input for the ask_question MCP tool."""

    question: str = Field(
        ...,
        min_length=3,
        max_length=2000,
        description="Natural language business question.",
    )
    user_id: str = Field(
        default="mcp-client",
        description="Caller identifier for audit logs.",
    )


# ── MCP Tool adapter ───────────────────────────────────────────────────────────

class AskToolAdapter(AbstractTool):

    def __init__(self, stream_reader: HttpStreamReader) -> None:
        self._reader = stream_reader

    # ── AbstractTool interface ─────────────────────────────────────────────────

    @property
    def input_schema(self) -> type[ToolInput]:
        return AskToolInput

    @property
    def definition(self) -> Tool:
        return Tool(
            name="ask_question",
            description=(
                "Ask a natural language business question about ecom data. "
                "The AI pipeline queries the semantic layer (dbt MetricFlow), "
                "retrieves context from Qdrant, and runs Trino queries if needed."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Business question in natural language.",
                        "minLength": 3,
                        "maxLength": 2000,
                    },
                    "user_id": {
                        "type": "string",
                        "description": "Caller identifier for audit logs.",
                        "default": "mcp-client",
                    },
                },
                "required": ["question"],
            },
        )

    async def _execute(self, validated: ToolInput) -> CallToolResult:
        """
        Build and execute the AskQuestion use case.

        Uses SilentStepCallback — steps are logged at DEBUG only.
        No Slack context available in MCP tool calls.
        """
        inp = validated  # type: ignore[assignment]

        gateway  = FastApiAskGatewayAdapter(stream_reader=self._reader)
        callback = SilentStepCallbackAdapter()
        use_case = AskQuestionUseCase(gateway=gateway, callback=callback)

        try:
            answer = await use_case.execute(
                question=inp.question,  # type: ignore[attr-defined]
                user_id=inp.user_id,    # type: ignore[attr-defined]
            )
            return success_result(answer)

        except EmptyStreamError as exc:
            logger.warning("Empty stream | %s", exc)
            return error_result(str(exc))
        
        except StreamError as exc:
            logger.error("Stream error | %s", exc)
            return error_result(str(exc))
