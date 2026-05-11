"""台灣地址正規化 — 全形半形、異體字、台↔臺、簡寫展開、縣→市 升格."""

from __future__ import annotations

import re
import unicodedata
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


# 縣市改制對應 (合併日: 2010-12-25; 桃園升格: 2014-12-25)
LEGACY_COUNTY_TO_CITY: dict[str, str] = {
    "高雄縣": "高雄市",  # 2010 與高雄市合併
    "臺北縣": "新北市",  # 2010 升格新北市
    "台北縣": "新北市",
    "臺中縣": "臺中市",  # 2010 與臺中市合併
    "台中縣": "臺中市",
    "臺南縣": "臺南市",  # 2010 與臺南市合併
    "台南縣": "臺南市",
    "桃園縣": "桃園市",  # 2014 升格
}

# 「巿、区、号」等異體字 → 「市、區、號」
_VARIANT_CHAR_MAP = str.maketrans(
    {
        "巿": "市",  # U+5DFF → U+5E02
        "区": "區",
        "号": "號",
        "弍": "二",
        "弐": "二",
        "参": "三",
        "肆": "四",
        "伍": "五",
        "陆": "六",
        "柒": "七",
        "捌": "八",
        "玖": "九",
    }
)

# 台→臺 標準化 (中華郵政官方用「臺」)
_TAI_NORMALIZE_PATTERNS = [
    (re.compile(r"台北市"), "臺北市"),
    (re.compile(r"台中市"), "臺中市"),
    (re.compile(r"台中縣"), "臺中縣"),
    (re.compile(r"台南市"), "臺南市"),
    (re.compile(r"台南縣"), "臺南縣"),
    (re.compile(r"台東縣"), "臺東縣"),
    (re.compile(r"台北縣"), "臺北縣"),
]


def normalize_address(addr: str, upgrade_legacy: bool = True) -> dict:
    """正規化台灣地址。

    步驟：
    1. NFKC 全形→半形 (數字/英文)
    2. 異體字 → 標準字 (巿→市, 区→區, 号→號)
    3. 台→臺 (郵政標準)
    4. (選配) 舊縣名 → 新市名 (高雄縣→高雄市 等)
    """
    if not addr:
        return {"valid": False, "reason": "空字串"}
    original = addr
    # 1. NFKC: 全形數字/字母 → 半形
    s = unicodedata.normalize("NFKC", addr)
    # 2. 異體字統一
    s = s.translate(_VARIANT_CHAR_MAP)
    # 3. 台 → 臺 (僅針對縣市)
    for pat, repl in _TAI_NORMALIZE_PATTERNS:
        s = pat.sub(repl, s)
    # 4. 移除多餘空白
    s = re.sub(r"\s+", "", s).strip()
    # 5. 舊縣名升格
    upgraded = False
    legacy_used: str | None = None
    if upgrade_legacy:
        for legacy, modern in LEGACY_COUNTY_TO_CITY.items():
            if s.startswith(legacy):
                s = modern + s[len(legacy) :]
                upgraded = True
                legacy_used = legacy
                break
    return {
        "valid": True,
        "original": original,
        "normalized": s,
        "upgraded_legacy_county": upgraded,
        "legacy_alias_detected": legacy_used,
    }


def align_legacy_county(name: str) -> dict:
    """舊縣名 → 現市名 (高雄縣→高雄市 等)。回傳改制年。"""
    aliases = {
        "高雄縣": ("高雄市", 2010, "與高雄市合併"),
        "臺北縣": ("新北市", 2010, "升格為新北市"),
        "台北縣": ("新北市", 2010, "升格為新北市"),
        "臺中縣": ("臺中市", 2010, "與臺中市合併"),
        "台中縣": ("臺中市", 2010, "與臺中市合併"),
        "臺南縣": ("臺南市", 2010, "與臺南市合併"),
        "台南縣": ("臺南市", 2010, "與臺南市合併"),
        "桃園縣": ("桃園市", 2014, "升格為直轄市"),
    }
    canonical = name.replace("台", "臺")
    target = aliases.get(name) or aliases.get(canonical)
    if target is None:
        return {"aligned": False, "input": name, "current_name": name}
    new_name, year, reason = target
    return {
        "aligned": True,
        "input": name,
        "current_name": new_name,
        "merger_year": year,
        "reason": reason,
    }


def register(mcp: FastMCP) -> None:
    @mcp.tool()
    def normalize_taiwan_address(addr: str, upgrade_legacy: bool = True) -> dict:
        """正規化台灣地址：全形→半形、巿/区/号 異體字、台→臺、(選配) 舊縣名升格."""
        return normalize_address(addr, upgrade_legacy=upgrade_legacy)

    @mcp.tool()
    def align_legacy_county_tool(name: str) -> dict:
        """舊縣名 → 現市名 (高雄縣→高雄市 等)。回傳改制年 + 說明."""
        return align_legacy_county(name)
