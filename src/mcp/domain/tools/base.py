from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, final

from mcp.types import CallToolResult, TextContent, Tool
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


# ── Input contract ─────────────────────────────────────────────────────────────

class ToolInput(BaseModel):
    """
    Base class for all tool input schemas.

    Rules:
      - Subclass this for every tool's input
      - frozen=True: inputs are immutable once validated — no mutation bugs
      - Pydantic validates at instantiation — failures surface before any I/O

    Example:
        class AskToolInput(ToolInput):
            question: str = Field(..., min_length=3)
            user_id: str
    """
    model_config = {"frozen": True}


# ── Result helpers ─────────────────────────────────────────────────────────────

def success_result(text: str) -> CallToolResult:
    """Build a successful CallToolResult with a plain text payload."""
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        isError=False,
    )


def error_result(message: str) -> CallToolResult:
    """Build an error CallToolResult with a descriptive message."""
    return CallToolResult(
        content=[TextContent(type="text", text=message)],
        isError=True,
    )


# ── Abstract base ──────────────────────────────────────────────────────────────

class AbstractTool(ABC):
    """
    Contract every MCP tool must satisfy.

    Subclasses implement three things:
      input_schema → Pydantic model class that validates raw arguments
      definition   → MCP Tool descriptor (name, description, JSON schema)
      _execute()   → business logic, receives a guaranteed-valid ToolInput

    The public execute() method is @final — it owns the pipeline:
      1. Validate input (Pydantic)
      2. Call _execute()
      3. Catch any unhandled exception → error_result (never crash the server)

    Subclasses can never override execute() — all logic goes in _execute().
    """

    @property
    @abstractmethod
    def input_schema(self) -> type[ToolInput]:
        """Pydantic model class used to validate raw MCP call arguments."""
        ...

    @property
    @abstractmethod
    def definition(self) -> Tool:
        """
        MCP Tool descriptor sent to clients on list_tools.

        The inputSchema field must mirror the fields in input_schema —
        MCP clients use it to build and validate their calls.
        """
        ...

    @abstractmethod
    async def _execute(self, validated: ToolInput) -> CallToolResult:
        """
        Business logic — called with guaranteed-valid, immutable input.

        Any exception raised here is caught by execute() and converted
        to an error_result. The MCP server will never crash from a tool.
        """
        ...

    @final
    async def execute(self, arguments: dict[str, Any]) -> CallToolResult:
        """
        Public entry point — called by the MCP server for every tool call.

        Pipeline:
          1. Validate raw arguments with input_schema (Pydantic)
             → validation error: return error_result, log WARNING (caller's fault)
          2. Call _execute() with the validated ToolInput
             → unexpected exception: return error_result, log ERROR (our fault)

        @final: this pipeline cannot be bypassed or overridden by subclasses.
        """
        # Step 1 — validate strictly before any I/O
        try:
            validated = self.input_schema.model_validate(arguments)
        except ValidationError as exc:
            logger.warning(
                "Tool '%s' received invalid input: %s",
                self.definition.name,
                exc,
            )
            return error_result(
                f"Invalid input for tool '{self.definition.name}': {exc}"
            )

        # Step 2 — run business logic, catch anything unexpected
        try:
            return await self._execute(validated)
        except Exception as exc:
            logger.exception(
                "Tool '%s' raised an unexpected error",
                self.definition.name,
            )
            return error_result(
                f"Tool '{self.definition.name}' encountered an internal error: {exc}"
            )