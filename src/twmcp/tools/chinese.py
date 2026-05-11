"""中文簡↔繁 + 阿拉伯↔中文數字."""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


def _get_opencc(variant: str):
    from opencc import OpenCC

    return OpenCC(variant)


def simplified_to_traditional(text: str, variant: Literal["zh-tw", "zh-hk"] = "zh-tw") -> str:
    """簡體中文轉繁體。variant: 'zh-tw' (台灣正體, 預設) | 'zh-hk' (香港繁體)."""
    config = "s2tw" if variant == "zh-tw" else "s2hk"
    return _get_opencc(config).convert(text)


def traditional_to_simplified(text: str) -> str:
    """繁體中文轉簡體 (tw2s)."""
    return _get_opencc("tw2s").convert(text)


def format_chinese_numerals(
    text: str | int | float,
    direction: Literal["arabic_to_chinese", "chinese_to_arabic"] = "arabic_to_chinese",
    upper: bool = False,
    variant: Literal["zh-tw", "zh-cn"] = "zh-tw",
) -> str:
    """阿拉伯數字 ↔ 中文 (公文/合約/支票場景)。

    upper=True 用大寫 (壹貳參).
    variant='zh-tw' (預設) 自動轉繁體：壹萬參仟伍佰；'zh-cn' 保留簡體：壹万叁仟伍佰.
    """
    import cn2an

    if direction == "arabic_to_chinese":
        mode = "up" if upper else "low"
        out = cn2an.an2cn(text, mode)
        if variant == "zh-tw":
            out = simplified_to_traditional(out, variant="zh-tw")
        return out
    return str(cn2an.cn2an(str(text), "smart"))


def register(mcp: "FastMCP") -> None:
    @mcp.tool()
    def simplified_to_traditional_tool(text: str, variant: str = "zh-tw") -> str:
        """簡體中文轉繁體。variant: 'zh-tw' (預設) 或 'zh-hk'."""
        v: Literal["zh-tw", "zh-hk"] = "zh-tw" if variant != "zh-hk" else "zh-hk"
        return simplified_to_traditional(text, variant=v)

    @mcp.tool()
    def traditional_to_simplified_tool(text: str) -> str:
        """繁體中文轉簡體。"""
        return traditional_to_simplified(text)

    @mcp.tool()
    def format_chinese_numerals_tool(
        text: str,
        direction: str = "arabic_to_chinese",
        upper: bool = False,
        variant: str = "zh-tw",
    ) -> str:
        """阿拉伯數字 ↔ 中文 (公文/合約/支票場景).

        direction='arabic_to_chinese' (預設) 或 'chinese_to_arabic'.
        upper=True 用大寫 (壹貳參).
        variant='zh-tw' (預設, 繁體) 或 'zh-cn' (簡體).
        """
        d: Literal["arabic_to_chinese", "chinese_to_arabic"]
        d = "chinese_to_arabic" if direction == "chinese_to_arabic" else "arabic_to_chinese"
        v: Literal["zh-tw", "zh-cn"] = "zh-cn" if variant == "zh-cn" else "zh-tw"
        return format_chinese_numerals(text, direction=d, upper=upper, variant=v)
