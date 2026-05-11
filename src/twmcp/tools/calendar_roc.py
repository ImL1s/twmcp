"""ROC 民國年 ↔ 西元 年份/日期轉換."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


_ROC_FORMATS = (
    # "114"
    re.compile(r"^(?P<y>\d{1,3})$"),
    # "114-05-04" or "114/05/04"
    re.compile(r"^(?P<y>\d{1,3})[-/](?P<m>\d{1,2})[-/](?P<d>\d{1,2})$"),
    # "114年5月4日"
    re.compile(r"^(?P<y>\d{1,3})年(?P<m>\d{1,2})月(?P<d>\d{1,2})日$"),
    # "1140504" (3+2+2 packed)
    re.compile(r"^(?P<y>\d{3})(?P<m>\d{2})(?P<d>\d{2})$"),
)

_WEST_FORMATS = (
    re.compile(r"^(?P<y>\d{4})$"),
    re.compile(r"^(?P<y>\d{4})[-/](?P<m>\d{1,2})[-/](?P<d>\d{1,2})$"),
    re.compile(r"^(?P<y>\d{4})年(?P<m>\d{1,2})月(?P<d>\d{1,2})日$"),
)


def roc_to_western(roc: str) -> dict:
    """民國年 → 西元年. 支援 '114' / '114-05-04' / '114年5月4日' / '1140504'."""
    s = roc.strip()
    for pat in _ROC_FORMATS:
        m = pat.fullmatch(s)
        if not m:
            continue
        y = int(m.group("y"))
        if y < 1:
            return {"valid": False, "reason": "民國年必須 >= 1"}
        west_year = y + 1911
        parts = m.groupdict()
        if "m" in parts and parts.get("m"):
            mm, dd = int(parts["m"]), int(parts["d"])
            return {
                "valid": True,
                "western_year": west_year,
                "month": mm,
                "day": dd,
                "iso_date": f"{west_year:04d}-{mm:02d}-{dd:02d}",
            }
        return {"valid": True, "western_year": west_year}
    return {"valid": False, "reason": "格式錯誤"}


def western_to_roc(western: str | int) -> dict:
    """西元年 → 民國年. 支援 2025 / '2025' / '2025-05-04' / '2025年5月4日'."""
    if isinstance(western, int):
        western = str(western)
    s = western.strip()
    for pat in _WEST_FORMATS:
        m = pat.fullmatch(s)
        if not m:
            continue
        y = int(m.group("y"))
        if y < 1912:
            return {"valid": False, "reason": "西元年必須 >= 1912"}
        roc_y = y - 1911
        parts = m.groupdict()
        if "m" in parts and parts.get("m"):
            mm, dd = int(parts["m"]), int(parts["d"])
            return {
                "valid": True,
                "roc_year": roc_y,
                "month": mm,
                "day": dd,
                "roc_formatted": f"{roc_y}年{mm}月{dd}日",
            }
        return {"valid": True, "roc_year": roc_y, "roc_formatted": f"民國{roc_y}年"}
    return {"valid": False, "reason": "格式錯誤"}


def register(mcp: "FastMCP") -> None:
    @mcp.tool()
    def roc_year_to_western_tool(roc: str) -> dict:
        """民國年 → 西元年. 支援 '114' / '114-05-04' / '114年5月4日' / '1140504' 等格式."""
        return roc_to_western(roc)

    @mcp.tool()
    def western_year_to_roc_tool(western: str) -> dict:
        """西元年 → 民國年. 支援 '2025' / '2025-05-04' / '2025年5月4日' 等格式."""
        return western_to_roc(western)
