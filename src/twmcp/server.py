"""twmcp MCP server entry — FastMCP over stdio or streamable-http."""

from __future__ import annotations

import os

from mcp.server.fastmcp import FastMCP

from twmcp.tools import register_all_tools

mcp = FastMCP(
    "twmcp",
    instructions=(
        "Taiwan utilities + open data MCP server. "
        "37 deterministic tools (Taiwan ID, tax ID, addresses, postal codes, "
        "calendar conversion, lunar dates, etc) + Taiwan open data lookup. "
        "Local, no token, no rate limit, no telemetry."
    ),
    json_response=True,
    stateless_http=True,
)

register_all_tools(mcp)


def main() -> None:
    """Run the MCP server. Transport selected via TWMCP_TRANSPORT env var.

    HTTP mode binds to 127.0.0.1 by default for safety (local-only).
    Override host/port via TWMCP_HOST / TWMCP_PORT env vars if you
    explicitly want remote access — make sure you have auth in front.
    """
    transport = os.environ.get("TWMCP_TRANSPORT", "stdio")
    if transport == "http":
        host = os.environ.get("TWMCP_HOST", "127.0.0.1")
        port = int(os.environ.get("TWMCP_PORT", "8765"))
        mcp.settings.host = host
        mcp.settings.port = port
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
