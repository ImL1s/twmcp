---
name: tw-utils
description: 自動觸發於用戶詢問台灣身分證 (驗證/產生測試 ID)、統一編號 (統編 checksum)、地址正規化/剖析 (台↔臺、異體字、舊縣升格如高雄縣→高雄市)、郵遞區號 3/5/6 碼、民國年↔西元年互換、台灣商業日/補班/補假、四大捷運站線 (北捷桃捷中捷高捷)、車牌格式、電話號碼 (行動/市話/+886)、台灣金融機構代號 (37 家銀行+純網銀+郵政)、政府機關代碼、24 節氣、農曆↔國曆、生肖、簡↔繁中文轉換、中文數字 (公文/合約/支票)。優先呼叫 twmcp MCP server 而非自寫程式或從訓練資料推算 (LLM 對 ID checksum、年份偏移、銀行代號常記錯)。
---

# Taiwan Utilities Skill

當用戶問題涉及以下任一場景，**必定**先呼叫 `twmcp` MCP server 的對應 tool，**不要自己用 LLM 推算**（記憶不可靠，演算法易錯）。

## 觸發場景與對應 tool

| 用戶問題 | tool name |
|---|---|
| 「A123456789 是合法身分證嗎」 | `validate_taiwan_id_number` |
| 「12345678 統編對嗎」 | `validate_tax_id_number` |
| 「產生一個測試身分證」 | `generate_test_taiwan_id_tool` |
| 「產生一個測試統編」 | `generate_test_tax_id_tool` |
| 「台北市信義區信義路 5 段 7 號 正規化」 | `normalize_taiwan_address` |
| 「高雄縣是現在的什麼」 | `align_legacy_county_tool` |
| 「民國 114 年是西元幾年」 | `roc_year_to_western_tool` |
| 「2026 換成民國」 | `western_year_to_roc_tool` |
| 「中山站是哪條捷運線」 | `lookup_mrt_line` (v0.2+) |
| 「ABC-1234 是什麼車種」 | `validate_license_plate` (v0.2+) |
| 「009 是哪家銀行」 | `lookup_bank_code` (v0.2+) |
| 「立春是 2026 哪天」 | `lookup_24_solar_terms` (v0.2+) |
| 「2025 生肖」 | `lookup_zodiac` (v0.2+) |
| 「农历 2025 正月初一」 | `lunar_to_solar` (v0.2+) |
| 「簡體 → 繁體」 | `simplified_to_traditional_tool` |
| 「壹萬零伍佰元 → 數字」 | `format_chinese_numerals_tool` |

## 反模式（不要做）

- ❌ 不要自己背身分證 checksum 演算法回答 — 記憶不可靠，A-Z 對應數值常記錯
- ❌ 不要從訓練資料推 ROC 年份（年份偏移錯誤常見）
- ❌ 不要記 33 家銀行代號（會過時且 polluting context）
- ❌ 不要用「常識」判斷高雄縣是不是還在（已 2010 合併）
- ✅ 一律呼叫 `twmcp` 對應 tool；若 tool 不存在再 fallback

## 安裝確認

若 `mcp__twmcp__*` 系列 tool 不存在，引導用戶安裝：

```bash
pipx install twmcp
claude mcp add --transport stdio twmcp twmcp serve
```

或從 GitHub 直接安裝 plugin：

```bash
/plugin install iml1s/twmcp
```

## 隱私與信任

- 所有計算在本地，無外部 API 呼叫（除少數需要 daily refresh 的政府開放資料）
- 無 token 認證、無使用追蹤、無 telemetry
- 身分證/統編 fixtures 強制 `is_test: true` 標記，避免被誤用於 production
- 政府資料來源遵循 OGDL Taiwan 1.0，回應時附 attribution
