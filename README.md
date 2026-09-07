# twmcp

[![CI](https://github.com/iml1s/twmcp/actions/workflows/ci.yml/badge.svg)](https://github.com/iml1s/twmcp/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)

> Taiwan utilities + open-data MCP server — **open-source, local, no token, no rate limit, no telemetry**.
> Drop-in alternative to [hub.twinkleai.tw](https://hub.twinkleai.tw/).

## Why

Twinkle Hub 是閉源 SaaS MCP proxy — 每個 query 經他們 server、`sk-...` Bearer token 計費、未來 pay-as-you-go。
所有 37 個 tool 的演算法已標 MIT、所有資料是政府公開資料（OGDL Taiwan 1.0）。
**沒有理由把資料主權交出去**。

|  | hub.twinkleai.tw | twmcp |
|---|---|---|
| Hosting | SaaS proxy | 本地 |
| Auth | `sk-...` Bearer token | 無 |
| Cost | Pay-as-you-go (planned) | Free, MIT |
| Privacy | Queries 經其 server | 純本地計算 |
| SLA | 99.5% (Pro tier) | 100% (你跑你的) |
| Lock-in | 透過其 `.json` 設定鎖定 | MCP / CLI / Skill / Plugin 四層任選 |
| Telemetry | 未知 | 零 SDK，承諾不加 |

Twinkle Hub 官方在 [pricing 頁](https://hub.twinkleai.tw/en/pricing)寫：

> "Twinkle Hub is an MCP endpoint, not an SDK ... MCP is open protocol;
> **rolling your own or going elsewhere is always an option**."

這個 repo 就是「rolling our own」。

## Quick start

```bash
# 從 git 跑（v0.1，PyPI 未發布前的推薦方式）
git clone https://github.com/iml1s/twmcp && cd twmcp
uvx --from . twmcp serve

# 發布 PyPI 後（v0.2+）
uvx twmcp serve
# 或常駐
pipx install twmcp && twmcp serve
```

## 註冊到 MCP client

**Claude Code** — 在 repo root 直接跑 `claude`，會自動讀 `.mcp.json` 啟動 server。或全域註冊：

```bash
claude mcp add --transport stdio twmcp -- uvx twmcp serve
```

**Claude Desktop** (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{ "mcpServers": { "twmcp": { "command": "uvx", "args": ["twmcp", "serve"] } } }
```

**Cursor** (`~/.cursor/mcp.json`):

```json
{ "mcpServers": { "twmcp": { "command": "uvx", "args": ["twmcp", "serve"] } } }
```

**Cline / Continue / 其他 MCP client** — 同上 stdio command 格式，加進該 client 的 MCP config。

## CLI（不用 LLM）

```bash
twmcp id A123456789                           # 驗證身分證 + 縣市判讀
twmcp tax-id 12345675 --rule pre-2023         # 驗證 8 碼統編 checksum
twmcp addr-normalize "高雄縣鳳山區某路1號"     # 全形/異體字/舊縣升格
twmcp roc-to-year 114-05-04                   # 民國 → 西元
twmcp num 12345 --upper                       # → 壹萬貳仟參佰肆拾伍
twmcp gen-id --seed 7                         # 產 test fixture (含 is_test=True)
twmcp serve --transport http                  # HTTP mode，綁 127.0.0.1:8765
twmcp --help                                  # 看全部
```

範例輸出：

```json
$ twmcp id A123456789
{
  "valid": true,
  "type": "national",
  "sex": "male",
  "issued_county_code": "A",
  "issued_county_hint": "臺北市"
}

$ twmcp addr-normalize "高雄縣鳳山區某路1號"
{
  "valid": true,
  "original": "高雄縣鳳山區某路1號",
  "normalized": "高雄市鳳山區某路1號",
  "upgraded_legacy_county": true,
  "legacy_alias_detected": "高雄縣"
}
```

## Tools

**v0.1（已實作，11 個純函式 tools，無外部呼叫）：**

| Tool | 用途 |
|---|---|
| `validate_taiwan_id_number` | 身分證/統一證號 checksum + 縣市判讀（含 1995-2020 舊式、2021+ 新式外來人口） |
| `validate_tax_id_number` | 8 碼統編 checksum（`post-2023` mod 5 / `pre-2023` mod 10 / `both`） |
| `generate_test_taiwan_id_tool` | 產通過 checksum 的測試身分證（強制 `is_test: true`） |
| `generate_test_tax_id_tool` | 產通過 checksum 的測試統編 |
| `normalize_taiwan_address` | 全形→半形、異體字（巿/区/号）統一、台→臺、舊縣升格 |
| `align_legacy_county_tool` | 高雄縣→高雄市、台北縣→新北市、桃園縣→桃園市… 含改制年 |
| `roc_year_to_western_tool` | 民國 → 西元，支援 `114` / `114-05-04` / `114年5月4日` / `1140504` |
| `western_year_to_roc_tool` | 西元 → 民國 |
| `simplified_to_traditional_tool` | 簡 → 繁（`zh-tw` 台灣正體 / `zh-hk` 香港繁體） |
| `traditional_to_simplified_tool` | 繁 → 簡 |
| `format_chinese_numerals_tool` | 阿拉伯↔中文，支援大寫（壹貳參）、繁/簡（公文/合約/支票場景） |

**Roadmap — 預計補到 ~37 tools：**

| 版本 | 範圍 |
|---|---|
| v0.2 | 商業日、國定假日、捷運站線、銀行代號、政府機關代碼、24 節氣、農曆↔國曆、生肖 |
| v0.3 | 郵遞區號 (3/5/6 碼)、行政區查詢、車牌、電話、MOEA 統編查公司、地址中英譯 |
| v0.4 | `data.gov.tw` FTS5 catalog 索引（52,960 datasets） |
| v0.5 | PCC 政府電子採購 daily sync |
| v0.6 | PDF 三件套、URL→markdown、IANA 時區、秒數人類化 |
| v0.7 | Claude Code plugin marketplace 上架 |
| v1.0 | 19 domains 全覆蓋 + 可選 Web UI |

## 資料來源

公開政府開放資料，遵循 OGDL Taiwan 1.0：

- [data.gov.tw](https://data.gov.tw/) — 52,960 datasets
- [中華郵政 TOWN_MOI.kml](https://www.post.gov.tw/post/download/TOWN_MOI.kml) — 郵遞區號 + 行政區
- [行政院人事行政總處辦公日曆](https://data.gov.tw/dataset/14718)（2024-2025 含補班；2026+ 取消補假）
- [FISC 銀行代號](https://www.fisc.com.tw/TC/OPENDATA/R1_MEMBER.csv)（含純網銀+郵政）
- [FSC 金融機構](https://stat.fsc.gov.tw/FSC_OAS3_RESTORE/api/CSV_EXPORT?TableID=B14)
- [MOEA 商工資料](https://data.gcis.nat.gov.tw/)
- [TDX 運輸資料](https://tdx.transportdata.tw/)
- [PCC 政府電子採購網](https://web.pcc.gov.tw/)

每個資料 tool response 都附 attribution (來源 URL + 機關 + license)。

## 隱私

- 所有計算在本地；除少數需 daily refresh 的政府資料外，無外部 API 呼叫
- 無 token、無 cookie、無使用追蹤、**承諾不加 telemetry SDK**
- 身分證/統編測試 fixtures 強制 `is_test: true` — 避免被誤用為真實 PII
- HTTP transport 預設綁 `127.0.0.1`（不是 `0.0.0.0`），不放外網

## Development

需 Python ≥ 3.11。CI 跑 3.11 / 3.12 / 3.13 矩陣。

```bash
git clone https://github.com/iml1s/twmcp && cd twmcp
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

pytest                  # 56 tests
ruff check src tests
ruff format src tests
```

新增 tool 的標準流程、編碼慣例、政府 API 端點清單、設計決策、外部 LLM 研究來源見 [`CLAUDE.md`](CLAUDE.md)。

---

## 支持

如果這個專案幫你省了點時間，可以[請我喝杯咖啡](https://buymeacoffee.com/iml1s)。

## License

- 程式碼：[MIT](LICENSE)
- 資料：OGDL Taiwan 1.0 passthrough + 各 dataset 原始 license
- 命名：`twmcp` — 避開 Twinkle 商標

## Acknowledgments

設計過程動員多個 AI 編組互相驗證：Claude Opus 4.7（1M context）、Cursor Grok 4.3、Codex GPT-5.5、Gemini 2.5 Pro、Gemini 3.1 Pro Preview、BrightData MCP。各家負責不同 angle（封裝設計、套件考古、政府 API 實測、Tool Schema 風險評估、SaaS SPA 深抓），彼此補盲點 + 對齊共識。完整 provenance 見 [`CLAUDE.md`](CLAUDE.md#研究編組與貢獻-multi-ai-provenance) 與 `docs/`。
