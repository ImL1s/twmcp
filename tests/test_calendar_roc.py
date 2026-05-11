"""ROC 民國年 ↔ 西元年 轉換邊界測試."""

from __future__ import annotations

import pytest

from twmcp.tools.calendar_roc import roc_to_western, western_to_roc


class TestRocToWestern:
    @pytest.mark.parametrize(
        "roc,expected_year",
        [
            ("114", 2025),
            ("1", 1912),
            ("113", 2024),
        ],
    )
    def test_year_only(self, roc, expected_year):
        r = roc_to_western(roc)
        assert r["valid"]
        assert r["western_year"] == expected_year

    def test_dash_format(self):
        r = roc_to_western("114-05-04")
        assert r["valid"]
        assert r["iso_date"] == "2025-05-04"

    def test_chinese_format(self):
        r = roc_to_western("114年5月4日")
        assert r["valid"]
        assert r["iso_date"] == "2025-05-04"

    def test_packed_format(self):
        r = roc_to_western("1140504")
        assert r["valid"]
        assert r["iso_date"] == "2025-05-04"

    def test_negative_year_invalid(self):
        r = roc_to_western("0")
        assert r["valid"] is False

    def test_invalid_format(self):
        r = roc_to_western("hello")
        assert r["valid"] is False


class TestWesternToRoc:
    def test_year_only(self):
        r = western_to_roc("2025")
        assert r["valid"]
        assert r["roc_year"] == 114

    def test_dash_format(self):
        r = western_to_roc("2025-05-04")
        assert r["valid"]
        assert r["roc_year"] == 114
        assert r["month"] == 5
        assert r["day"] == 4

    def test_before_1912_invalid(self):
        r = western_to_roc("1911")
        assert r["valid"] is False

    def test_integer_input(self):
        r = western_to_roc(2025)
        assert r["valid"]
        assert r["roc_year"] == 114

    def test_invalid(self):
        r = western_to_roc("not a year")
        assert r["valid"] is False
