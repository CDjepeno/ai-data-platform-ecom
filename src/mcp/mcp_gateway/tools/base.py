
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, final

from mcp.types import CallToolResult, TextContent, Tool
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)


# ── Input contract ─────────────────────────────────────────────────────────────

class ToolInput(BaseModel):
    model_config = {"frozen": True}  # inputs are immutable once validated


# ── Tool result helpers ────────────────────────────────────────────────────────

def success_result(text: str) -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        isError=False,
    )


def error_result(message: str) -> CallToolResult:
    return CallToolResult(
        content=[TextContent(type="text", text=message)],
        isError=True,
    )


# ── Abstract base ──────────────────────────────────────────────────────────────

class AbstractTool(ABC):

    @property
    @abstractmethod
    def input_schema(self) -> type[ToolInput]:
        """
        Return the Pydantic model class that validates raw MCP arguments.
        Must be a subclass of ToolInput.
        """
        ...

    @property
    @abstractmethod
    def definition(self) -> Tool: ...

    @abstractmethod
    async def _execute(self, validated: ToolInput) -> CallToolResult:
        ...

    # ── Final pipeline — never override ───────────────────────────────────────

    @final
    async def execute(self, arguments: dict[str, Any]) -> CallToolResult:

        try:
            validated = self.input_schema.model_validate(arguments)
        except ValidationError as exc:
            # Validation errors are the caller's fault — log at WARNING not ERROR
            logger.warning(
                "Tool '%s' received invalid input: %s",
                self.definition.name,
                exc,
            )
            return error_result(
                f"Invalid input for tool '{self.definition.name}': {exc}"
            )

        # Step 2 — run business logic, catch anything that leaks out
        try:
            return await self._execute(validated)
        except Exception as exc:
            # Unexpected errors are our fault — log at ERROR with full traceback
            logger.exception(
                "Tool '%s' raised an unexpected error",
                self.definition.name,
            )
            return error_result(
                f"Tool '{self.definition.name}' encountered an internal error: {exc}"
            )