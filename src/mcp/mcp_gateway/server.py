from __future__ import annotations

import asyncio
import logging
import logging.config
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    TextContent,
    Tool,
)

from adapters.ecom.ask_tool import AskTool
from mcp_gateway.config import Settings
from mcp_gateway.tools.base import AbstractTool, error_result

logger = logging.getLogger(__name__)


# ── Logging setup ──────────────────────────────────────────────────────────────

def _configure_logging(level: str) -> None:

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%dT%H:%M:%S",
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "stream": "ext://sys.stderr",  # stdout is reserved for MCP stdio
                }
            },
            "root": {
                "handlers": ["console"],
                "level": level.upper(),
            },
        }
    )


# ── Server factory ─────────────────────────────────────────────────────────────

def build_server(settings: Settings) -> tuple[Server, httpx.AsyncClient]:
    """
    Wire settings + tools into a configured MCP Server instance.

    Separating construction from execution makes the server testable:
    tests call build_server() with mock settings, no subprocess needed.

    Args:
        settings: Validated pydantic-settings instance.

    Returns:
        Tuple of (Server, AsyncClient) — the client is returned so the
        caller can manage its lifecycle (close on shutdown).
    """
    app = Server("mcp-gateway")

    # Single shared HTTP client — connection pool reused across all tool calls
    http_client = httpx.AsyncClient(
        base_url=str(settings.fastapi_base_url),
        timeout=httpx.Timeout(settings.mcp_http_timeout),
        headers={"Content-Type": "application/json"},
    )

    # ── Register tools ─────────────────────────────────────────────────────────
    # To add a new tool: instantiate it here and append to this list.
    # The handlers below never need to change — Open/Closed principle.
    tools: list[AbstractTool] = [
        AskTool(http_client=http_client),
    ]

    # Index by name for O(1) dispatch
    registry: dict[str, AbstractTool] = {
        t.definition.name: t for t in tools
    }

    logger.info(
        "MCP server built | tools=%s | fastapi=%s",
        list(registry.keys()),
        settings.fastapi_base_url,
    )

    # ── MCP protocol handlers ──────────────────────────────────────────────────

    @app.list_tools()
    async def handle_list_tools() -> list[Tool]:
        """
        Return all registered tool descriptors.
        Called by MCP clients (Claude Desktop, Slack bot) on connect.
        """
        return [t.definition for t in tools]

    @app.call_tool()
    async def handle_call_tool(
        name: str,
        arguments: dict[str, Any],
    ) -> list[TextContent]:
        """
        Dispatch a tool call by name and return its content blocks.

        The AbstractTool.execute() pipeline handles:
          - Input validation (Pydantic)
          - Business logic (_execute)
          - Error catching (never crashes the server)
        """
        tool = registry.get(name)

        if tool is None:
            logger.warning("Unknown tool requested: %r", name)
            # Return an error content block — do not raise (would kill the server)
            return [
                TextContent(
                    type="text",
                    text=f"Unknown tool '{name}'. Available: {list(registry.keys())}",
                )
            ]

        result: CallToolResult = await tool.execute(arguments)

        # Extract TextContent blocks from the result
        return [
            block
            for block in result.content
            if isinstance(block, TextContent)
        ]

    return app, http_client


# ── Entry points ───────────────────────────────────────────────────────────────

async def main() -> None:
    """
    Async entry point — configures logging, builds the server, starts stdio.

    The stdio transport reads JSON-RPC from stdin and writes to stdout.
    This is why all logging goes to stderr — stdout is reserved for MCP protocol.
    """
    settings = Settings()
    _configure_logging(settings.log_level)

    logger.info("Starting MCP gateway server")

    app, http_client = build_server(settings)

    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP stdio transport ready — waiting for client")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )
    finally:
        # Always close the HTTP client cleanly — avoids ResourceWarning
        await http_client.aclose()
        logger.info("MCP gateway server stopped")


def main_sync() -> None:
    """
    Sync wrapper for the `mcp-server` Poetry script entry point.

    poetry run mcp-server → calls this → asyncio.run(main())
    """
    asyncio.run(main())