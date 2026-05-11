"""中華民國身分證 + 統一編號 — 公開演算法 derive, no PII lookup."""

from __future__ import annotations

import random
import re
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP


# 內政部身分證字母對應數值表 (含外國人 I/O)
ID_CODES: dict[str, int] = {
    "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "G": 16,
    "H": 17, "I": 34, "J": 18, "K": 19, "L": 20, "M": 21, "N": 22,
    "O": 35, "P": 23, "Q": 24, "R": 25, "S": 26, "T": 27, "U": 28,
    "V": 29, "W": 32, "X": 30, "Y": 31, "Z": 33,
}

_COUNTY_BY_LETTER: dict[str, str] = {
    "A": "臺北市", "B": "臺中市", "C": "基隆市", "D": "臺南市",
    "E": "高雄市", "F": "新北市", "G": "宜蘭縣", "H": "桃園市",
    "J": "新竹縣", "K": "苗栗縣", "L": "臺中縣(舊)", "M": "南投縣",
    "N": "彰化縣", "P": "雲林縣", "Q": "嘉義縣", "R": "臺南縣(舊)",
    "S": "高雄縣(舊)", "T": "屏東縣", "U": "花蓮縣", "V": "臺東縣",
    "X": "澎湖縣", "Y": "陽明山(廢)", "W": "金門縣", "Z": "連江縣",
    "I": "嘉義市", "O": "新竹市",
}


def _id_checksum_pass(letter: str, digits: list[int]) -> bool:
    code = ID_CODES[letter]
    total = code // 10 + (code % 10) * 9
    total += sum(d * w for d, w in zip(digits, [8, 7, 6, 5, 4, 3, 2, 1, 1]))
    return total % 10 == 0


def validate_taiwan_id(id_str: str, allow_foreigner: bool = True) -> dict:
    """驗證身分證字號 (本國) 或外國人統一證號 (舊式/新式)."""
    s = id_str.strip().upper()
    # 本國格式 [A-Z][12][0-9]{8}; 1995-2020 外國人舊式 [A-Z][AB-D][0-9]{8}
    # 2021+ 新式外來人口 [A-Z][89][0-9]{8} (Twinkle Hub 同此規則)
    if re.fullmatch(r"[A-Z][12][0-9]{8}", s):
        digits = [int(c) for c in s[1:]]
        if not _id_checksum_pass(s[0], digits):
            return {"valid": False, "reason": "checksum 不通過"}
        return {
            "valid": True,
            "type": "national",
            "sex": "male" if s[1] == "1" else "female",
            "issued_county_code": s[0],
            "issued_county_hint": _COUNTY_BY_LETTER.get(s[0]),
        }
    if allow_foreigner and re.fullmatch(r"[A-Z][89][0-9]{8}", s):
        digits = [int(c) for c in s[1:]]
        if not _id_checksum_pass(s[0], digits):
            return {"valid": False, "reason": "checksum 不通過"}
        return {
            "valid": True,
            "type": "foreigner_new",
            "sex": "male" if s[1] == "8" else "female",
            "issued_county_code": s[0],
        }
    if allow_foreigner and re.fullmatch(r"[A-Z][A-D][0-9]{8}", s):
        # 舊式 (1995-2020) — 第二碼字母對應 0/1，後 8 碼
        sex_code = ID_CODES[s[1]] % 10
        digits = [sex_code] + [int(c) for c in s[2:]]
        # 沿用本國驗算式
        if not _id_checksum_pass(s[0], digits):
            return {"valid": False, "reason": "checksum 不通過 (舊式外來)"}
        return {
            "valid": True,
            "type": "foreigner_legacy",
            "sex": "male" if sex_code == 0 else "female",
            "issued_county_code": s[0],
        }
    return {"valid": False, "reason": "格式錯誤"}


def generate_test_taiwan_id(
    sex: Literal["male", "female", None] = None,
    city_letter: str = "A",
    seed: int | None = None,
) -> dict:
    """產生通過 checksum 的測試身分證 (非真實 PII)."""
    rng = random.Random(seed)
    city_letter = city_letter.upper()
    if city_letter not in ID_CODES:
        return {"is_test": True, "valid": False, "reason": "city_letter 不合法"}
    if sex == "male":
        first = "1"
    elif sex == "female":
        first = "2"
    else:
        first = rng.choice(["1", "2"])
    body = [int(first)] + [rng.randrange(10) for _ in range(7)]
    code = ID_CODES[city_letter]
    total = code // 10 + (code % 10) * 9
    total += sum(d * w for d, w in zip(body, [8, 7, 6, 5, 4, 3, 2, 1]))
    check = (-total) % 10
    return {
        "is_test": True,
        "id_number": city_letter + "".join(map(str, body)) + str(check),
        "sex": "male" if first == "1" else "female",
        "issued_county_code": city_letter,
    }


def _tax_checksum_sum(s: str) -> int:
    weights = [1, 2, 1, 2, 1, 2, 4, 1]
    total = 0
    for ch, w in zip(s, weights):
        p = int(ch) * w
        total += p // 10 + p % 10
    return total


def validate_tax_id(
    tax_id: str, rule: Literal["post-2023", "pre-2023", "both"] = "post-2023"
) -> dict:
    """驗證 8 位統編 checksum (post-2023 mod 5; pre-2023 mod 10; both 取聯集)."""
    if not re.fullmatch(r"\d{8}", tax_id):
        return {"valid": False, "reason": "格式錯誤"}
    total = _tax_checksum_sum(tax_id)
    legacy_ok = total % 10 == 0 or (tax_id[6] == "7" and (total + 1) % 10 == 0)
    modern_ok = total % 5 == 0 or (tax_id[6] == "7" and (total + 1) % 5 == 0)
    if rule == "pre-2023":
        valid = legacy_ok
    elif rule == "post-2023":
        valid = modern_ok
    else:
        valid = legacy_ok or modern_ok
    return {
        "valid": valid,
        "rule_used": rule,
        "legacy_passed": legacy_ok,
        "post_2023_passed": modern_ok,
        "seventh_digit_special": tax_id[6] == "7",
    }


def generate_test_tax_id(
    rule: Literal["post-2023", "pre-2023"] = "post-2023",
    seed: int | None = None,
) -> dict:
    """產生通過 checksum 的測試統編 (非真實註冊)."""
    rng = random.Random(seed)
    for _ in range(10_000):
        s = "".join(str(rng.randrange(10)) for _ in range(8))
        if validate_tax_id(s, rule=rule)["valid"]:
            return {"is_test": True, "tax_id": s, "rule": rule}
    return {"is_test": True, "valid": False, "reason": "exhausted"}


def register(mcp: "FastMCP") -> None:
    @mcp.tool()
    def validate_taiwan_id_number(id_number: str) -> dict:
        """驗證中華民國身分證字號或外國人統一證號 (公開演算法 derive, 無 PII lookup)."""
        return validate_taiwan_id(id_number)

    @mcp.tool()
    def validate_tax_id_number(tax_id: str, rule: str = "post-2023") -> dict:
        """驗證 8 位統一編號 checksum. rule='post-2023'(mod5, 預設) | 'pre-2023'(mod10) | 'both'."""
        rule_typed: Literal["post-2023", "pre-2023", "both"]
        if rule in ("post-2023", "pre-2023", "both"):
            rule_typed = rule  # type: ignore[assignment]
        else:
            rule_typed = "post-2023"
        return validate_tax_id(tax_id, rule=rule_typed)

    @mcp.tool()
    def generate_test_taiwan_id_tool(
        sex: str | None = None,
        city_letter: str = "A",
        seed: int | None = None,
    ) -> dict:
        """產生通過 checksum 的測試身分證 (非真實 PII; 結果含 is_test=True)."""
        s: Literal["male", "female", None]
        if sex in ("male", "female"):
            s = sex  # type: ignore[assignment]
        else:
            s = None
        return generate_test_taiwan_id(sex=s, city_letter=city_letter, seed=seed)

    @mcp.tool()
    def generate_test_tax_id_tool(rule: str = "post-2023", seed: int | None = None) -> dict:
        """產生通過 checksum 的測試統編 (非真實註冊; 結果含 is_test=True)."""
        r: Literal["post-2023", "pre-2023"]
        if rule in ("post-2023", "pre-2023"):
            r = rule  # type: ignore[assignment]
        else:
            r = "post-2023"
        return generate_test_tax_id(rule=r, seed=seed)
