from __future__ import annotations

import asyncio
from typing import Any

import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.server.stdio import stdio_server
from mcp.types import CallToolResult, TextContent, Tool
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route

from domain.tools.base import AbstractTool
from infrastructure.adapters.fast_api.http_stream_reader import HttpStreamReader
from infrastructure.adapters.mcp.ask_tool_adapter import AskToolAdapter
from infrastructure.config import settings
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
        "Building MCP server | transport=%s | fastapi=%s | timeout=%ss",
        settings.mcp_transport,
        settings.fastapi_base_url,
        settings.mcp_http_timeout,
    )

    http_client = create_http_client(settings)
    reader = HttpStreamReader(http_client=http_client)

    tools: list[AbstractTool] = [
        AskToolAdapter(stream_reader=reader),
    ]
    registry: dict[str, AbstractTool] = {
        t.definition.name: t for t in tools
    }

    app = Server("mcp-gateway")

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
            logger.warning("Unknown tool requested: %r", name)
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


# ── stdio transport — local CLI / Claude Desktop ───────────────────────────────

async def run_stdio(app: Server, http_client: Any) -> None:
    """
    stdio mode: communicates via stdin/stdout pipes.
    Used locally with Claude Desktop or direct CLI invocation.
    Process stays alive as long as the parent keeps stdin open.
    """
    logger.info("MCP transport=stdio — waiting for client on stdin")
    try:
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )
    finally:
        await http_client.aclose()
        logger.info("MCP gateway stopped (stdio)")


# ── SSE transport — Docker / Kubernetes ───────────────────────────────────────

async def run_sse(app: Server, http_client: Any) -> None:
    """
    SSE mode: listens on HTTP port, keeps process alive.
    Used in Docker Compose and Kubernetes — no parent process required.
    """
    logger.info(
        "MCP transport=sse — listening on 0.0.0.0:%d",
        settings.mcp_port,
    )

    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options(),
            )
        return Response()

    starlette_app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ]
    )

    config = uvicorn.Config(
        app=starlette_app,
        host="0.0.0.0",
        port=settings.mcp_port,
        log_level=settings.log_level.lower(),
    )
    server = uvicorn.Server(config)

    try:
        await server.serve()  # blocks until SIGTERM received
    finally:
        await http_client.aclose()
        logger.info("MCP gateway stopped (sse)")


# ── Entry point — transport selected from config ───────────────────────────────

async def main() -> None:
    """
    Select transport from MCP_TRANSPORT env var:
      stdio (default) → local development, Claude Desktop
      sse             → Docker Compose, Kubernetes
    """
    app, http_client = build_server()

    if settings.mcp_transport == "sse":
        await run_sse(app, http_client)
    elif settings.mcp_transport == "stdio":
        await run_stdio(app, http_client)
    else:
        raise ValueError(
            f"Unknown MCP_TRANSPORT={settings.mcp_transport!r}. "
            "Expected 'stdio' or 'sse'."
        )


def main_sync() -> None:
    """Sync entry point for `poetry run mcp-server`."""
    asyncio.run(main())


if __name__ == "__main__":
    main_sync()