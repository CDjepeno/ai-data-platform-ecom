from __future__ import annotations

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool

from infrastructure.config import settings
from adapters.ecom.ask_tool import AskToolAdapter
from domain.tools.base import AbstractTool
from infrastructure.adapters.fast_api.http_stream_reader import HttpStreamReader
from infrastructure.factory.client_factory import create_http_client
from infrastructure.logging.setup import configure_logging
from utils import get_logger

# ── Logging first — before any other module logs anything ─────────────────────
configure_logging(
    log_level=settings.log_level,
    json_logs=settings.json_logs,
)

logger = get_logger(__name__)


# ── Server factory ─────────────────────────────────────────────────────────────

def build_server() -> tuple[Server, Any]:

    logger.info(
        "Building MCP server | fastapi=%s | timeout=%ss",
        settings.fastapi_base_url,
        settings.mcp_http_timeout,
    )

    # ── Infrastructure ─────────────────────────────────────────────────────────
    http_client = create_http_client(settings)
    reader      = HttpStreamReader(http_client=http_client)

    # ── Tools registry ─────────────────────────────────────────────────────────
    tools: list[AbstractTool] = [
        AskToolAdapter(stream_reader=reader),
    ]
    registry: dict[str, AbstractTool] = {
        t.definition.name: t for t in tools
    }

    app = Server("mcp-gateway")

    # ── MCP protocol handlers ──────────────────────────────────────────────────

    @app.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return [t.definition for t in tools]

    @app.call_tool()
    async def handle_call_tool(
        name: str,
        arguments: dict[str, Any],
    ) -> list[TextContent]:
        tool = registry.get(name)

        if tool is None:
            logger.warning("Unknown tool: %r", name)
            return [TextContent(
                type="text",
                text=f"Unknown tool '{name}'. Available: {list(registry.keys())}",
            )]

        result: CallToolResult = await tool.execute(arguments)

        return [
            block for block in result.content
            if isinstance(block, TextContent)
        ]

    logger.info("MCP server ready | tools=%s", list(registry.keys()))

    return app, http_client


# ── Entry points ───────────────────────────────────────────────────────────────

async def main() -> None:
    """Start MCP server with stdio transport."""
    logger.info("Starting MCP gateway")

    app, http_client = build_server()

    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP stdio ready — waiting for client")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )
    finally:
        await http_client.aclose()
        logger.info("MCP gateway stopped")


def main_sync() -> None:
    """Sync entry point for `poetry run mcp-server`."""
    asyncio.run(main())