"""身分證 + 統編 checksum 邊界測試."""

from __future__ import annotations

import pytest

from twmcp.tools.tw_id import (
    generate_test_tax_id,
    generate_test_taiwan_id,
    validate_tax_id,
    validate_taiwan_id,
)


class TestTaiwanID:
    """身分證 checksum 驗證 (本國 + 外國人新舊式)."""

    def test_valid_national_male(self):
        # 已知合法身分證 (官方範例，非真實 PII)
        r = validate_taiwan_id("A123456789")
        assert r["valid"] is True
        assert r["type"] == "national"
        assert r["sex"] == "male"
        assert r["issued_county_code"] == "A"

    def test_invalid_checksum(self):
        r = validate_taiwan_id("A123456788")
        assert r["valid"] is False
        assert r["reason"] == "checksum 不通過"

    def test_invalid_format(self):
        r = validate_taiwan_id("X")
        assert r["valid"] is False

    def test_invalid_county_letter(self):
        # 縣市字母錯誤 (但是現在判 "格式錯誤" 也算合理 ─ 看 regex 前置濾)
        # 實際: 縣市字母錯時 ID_CODES.get(s[0]) 會 KeyError, 故 regex 先擋
        # 這裡測一個非數字 sex code 的情況
        r = validate_taiwan_id("A323456789")  # 第二碼 3 非 1/2/8/9
        assert r["valid"] is False

    @pytest.mark.parametrize("id_str", ["a123456789", " A123456789 "])
    def test_case_and_whitespace_tolerant(self, id_str):
        r = validate_taiwan_id(id_str)
        assert r["valid"] is True

    def test_generate_then_validate_loop(self):
        for seed in range(20):
            generated = generate_test_taiwan_id(seed=seed)
            assert generated["is_test"] is True
            assert validate_taiwan_id(generated["id_number"])["valid"]

    def test_generate_female(self):
        g = generate_test_taiwan_id(sex="female", city_letter="F", seed=42)
        assert g["sex"] == "female"
        assert g["id_number"].startswith("F2")
        assert validate_taiwan_id(g["id_number"])["valid"]

    def test_invalid_city_letter_in_generate(self):
        r = generate_test_taiwan_id(city_letter="@")
        assert r["valid"] is False


class TestTaxID:
    """統一編號 checksum (mod 5 post-2023 / mod 10 pre-2023)."""

    def test_valid_post_2023(self):
        # generate_test_tax_id 一定會回合法
        g = generate_test_tax_id(rule="post-2023", seed=1)
        assert validate_tax_id(g["tax_id"], rule="post-2023")["valid"]

    def test_valid_pre_2023(self):
        g = generate_test_tax_id(rule="pre-2023", seed=2)
        assert validate_tax_id(g["tax_id"], rule="pre-2023")["valid"]

    def test_invalid_format(self):
        r = validate_tax_id("1234567")
        assert r["valid"] is False
        assert r["reason"] == "格式錯誤"

    def test_invalid_non_digits(self):
        r = validate_tax_id("ABCDEFGH")
        assert r["valid"] is False

    def test_seventh_digit_seven_legacy(self):
        # 已知 12345675 第 7 碼為 7 (mod 10 加 1) — 用 generator 取例
        # 確保第 7 碼為 7 的 special path 不會回傳錯誤
        for seed in range(50):
            g = generate_test_tax_id(rule="pre-2023", seed=seed)
            if g["tax_id"][6] == "7":
                r = validate_tax_id(g["tax_id"], rule="pre-2023")
                assert r["valid"]
                assert r["seventh_digit_special"] is True
                break

    def test_both_rule(self):
        g_legacy = generate_test_tax_id(rule="pre-2023", seed=10)
        r = validate_tax_id(g_legacy["tax_id"], rule="both")
        assert r["valid"]

    def test_default_rule(self):
        g = generate_test_tax_id(seed=20)
        r = validate_tax_id(g["tax_id"])
        # 預設 rule=post-2023, 因 generator 也預設 post-2023, 應通過
        assert r["valid"]


class TestForeignerID:
    """外國人統一證號 (舊式 1995-2020 + 新式 2021+)."""

    def test_new_foreigner_format_check(self):
        # 新式: [A-Z][89][0-9]{8}
        # 8/9 為性別碼。我們不知道一個真實合法的 fixture，
        # 但可以確保格式拒絕錯誤 (這裡只是 smoke test)
        r = validate_taiwan_id("A800000000")
        # checksum 可能不通過，但 reason 不能是 "格式錯誤"
        assert r.get("reason") != "格式錯誤"

    def test_legacy_foreigner_format_check(self):
        # 舊式: [A-Z][A-D][0-9]{8}
        r = validate_taiwan_id("AA00000000")
        assert r.get("reason") != "格式錯誤"
