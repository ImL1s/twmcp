"""地址正規化邊界測試."""

from __future__ import annotations

from twmcp.tools.address import align_legacy_county, normalize_address


class TestNormalizeAddress:
    def test_basic(self):
        r = normalize_address("台北市信義路5段7號")
        assert r["valid"]
        assert "臺北市" in r["normalized"]

    def test_fullwidth_digits(self):
        r = normalize_address("臺北市信義路５段７號")
        assert "5段7號" in r["normalized"]

    def test_variant_chars(self):
        r = normalize_address("台北巿信義区信義路5段7号")
        assert "市" in r["normalized"]
        assert "區" in r["normalized"]
        assert "號" in r["normalized"]

    def test_legacy_county_upgrade(self):
        r = normalize_address("高雄縣鳳山區某路1號")
        assert r["valid"]
        assert r["upgraded_legacy_county"] is True
        assert r["normalized"].startswith("高雄市")
        assert r["legacy_alias_detected"] == "高雄縣"

    def test_legacy_county_no_upgrade(self):
        r = normalize_address("高雄縣鳳山區某路1號", upgrade_legacy=False)
        assert r["upgraded_legacy_county"] is False
        assert r["normalized"].startswith("高雄縣")

    def test_taipei_county_to_new_taipei(self):
        r = normalize_address("台北縣板橋區某路1號")
        assert r["normalized"].startswith("新北市")

    def test_taoyuan_county_to_city(self):
        r = normalize_address("桃園縣中壢區某路1號")
        assert r["normalized"].startswith("桃園市")

    def test_empty_input(self):
        r = normalize_address("")
        assert r["valid"] is False

    def test_whitespace_stripping(self):
        r = normalize_address("台北市  信義路   5段")
        assert " " not in r["normalized"]


class TestAlignLegacyCounty:
    def test_kaohsiung_county(self):
        r = align_legacy_county("高雄縣")
        assert r["aligned"]
        assert r["current_name"] == "高雄市"
        assert r["merger_year"] == 2010

    def test_taipei_county_simplified(self):
        r = align_legacy_county("台北縣")
        assert r["aligned"]
        assert r["current_name"] == "新北市"

    def test_taoyuan_county_upgrade_2014(self):
        r = align_legacy_county("桃園縣")
        assert r["aligned"]
        assert r["merger_year"] == 2014

    def test_no_alias(self):
        r = align_legacy_county("臺北市")
        assert r["aligned"] is False
        assert r["current_name"] == "臺北市"
