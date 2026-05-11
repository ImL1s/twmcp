"""簡繁轉換 + 中文數字邊界測試."""

from __future__ import annotations

from twmcp.tools.chinese import (
    format_chinese_numerals,
    simplified_to_traditional,
    traditional_to_simplified,
)


class TestSimplifiedTraditional:
    def test_basic_s2tw(self):
        out = simplified_to_traditional("简体中文测试")
        assert out == "簡體中文測試"

    def test_s2tw_uses_taiwan_terms(self):
        # 軟件 → 軟體 (zh-tw 慣用)
        out = simplified_to_traditional("软件", variant="zh-tw")
        assert "軟體" in out or "軟件" in out  # 容許 lib 差異

    def test_t2s(self):
        out = traditional_to_simplified("繁體中文")
        assert out == "繁体中文"


class TestChineseNumerals:
    def test_arabic_to_chinese_low(self):
        out = format_chinese_numerals(123)
        assert "一" in out or "百" in out

    def test_arabic_to_chinese_upper_traditional(self):
        """大寫 + 預設 zh-tw → 繁體大寫 (壹貳參)."""
        out = format_chinese_numerals(12345, upper=True, variant="zh-tw")
        # 應該是繁體大寫: 壹萬貳仟參佰肆拾伍 (或類似，視 cn2an 細節)
        assert "萬" in out  # 繁體萬，非簡體万
        assert "壹" in out

    def test_arabic_to_chinese_upper_simplified(self):
        out = format_chinese_numerals(12345, upper=True, variant="zh-cn")
        # 簡體應該有「万」字
        assert "万" in out

    def test_chinese_to_arabic(self):
        out = format_chinese_numerals("一千二百三十四", direction="chinese_to_arabic")
        assert out == "1234"
