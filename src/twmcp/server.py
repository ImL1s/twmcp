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
    """Run the MCP server. Transport selected via TWMCP_TRANSPORT env var."""
    transport = os.environ.get("TWMCP_TRANSPORT", "stdio")
    if transport == "http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
