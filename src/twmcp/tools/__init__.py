"""twmcp tools — auto-discovery and registration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from twmcp.tools import (
    address,
    calendar_roc,
    chinese,
    tw_id,
)

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


_TOOL_MODULES = (
    tw_id,
    address,
    calendar_roc,
    chinese,
)


def register_all_tools(mcp: "FastMCP") -> None:
    """Register every tool module's @mcp.tool() decorated functions."""
    for mod in _TOOL_MODULES:
        mod.register(mcp)
