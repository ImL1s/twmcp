# twmcp — Claude Code 工作指南

> Taiwan utilities + open-data MCP server. Drop-in 開源替代品 for [hub.twinkleai.tw](https://hub.twinkleai.tw/).
> 程式 MIT、資料 OGDL Taiwan 1.0。本地、無 token、無限流。

## 專案定位

替代閉源 SaaS hub.twinkleai.tw — 把 37 個 deterministic 台灣工具與 data.gov.tw 52,960 個資料集打包成本地 MCP server。
Twinkle Hub 各 tool 標 MIT、資料全為公開政府開放資料，**重做合法且鼓勵**（官方 pricing 頁親自說「rolling your own is always an option」）。

## 三層交付架構

| 層 | 角色 | 檔案 |
|---|---|---|
| **MCP server** | 核心計算層，跨 client（Cursor/Cline/Continue 都吃） | `src/twmcp/server.py` + `src/twmcp/tools/*` |
| **CLI** | 同邏輯 terminal 入口，給 CI/script/debug | `src/twmcp/cli.py` |
| **Skill** | 教 Claude 何時自動 invoke MCP | `skills/tw-utils/SKILL.md`, `skills/tw-data/SKILL.md` |
| **Plugin** | 一鍵打包 MCP + skill + commands + agent | `.claude-plugin/plugin.json` |

四層共享同一份 Python 邏輯。MCP 是 ground truth，其他三個是不同 surface。

## 開發指令

```bash
# 初始 setup (Python 3.11+, Homebrew Python 需 venv 以繞 PEP 668)
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 日常開發
pytest                      # 跑全部 tests (~56 個)
ruff check src tests        # lint
ruff format src tests       # 自動格式化
ruff check --fix src tests  # auto-fix lint

# CLI smoke
twmcp version
twmcp id A123456789
twmcp tax-id 12345675 --rule pre-2023
twmcp roc-to-year 114-05-04
twmcp addr-normalize "高雄縣鳳山區"
twmcp gen-id --seed 7

# 啟動 MCP server (Claude Code 會自動透過 .mcp.json 啟)
twmcp serve                 # stdio (預設)
TWMCP_TRANSPORT=http twmcp serve  # streamable-http (綁 127.0.0.1)
```

## 新增 tool 的標準流程

1. **新檔**：`src/twmcp/tools/<name>.py`
2. **純函式**：所有邏輯放 module-level `def`，**不要**寫進 `register()`
3. **註冊 wrapper**：在同檔加 `def register(mcp): @mcp.tool() def <tool_name>...`
4. **加進 registry**：編輯 `src/twmcp/tools/__init__.py` 的 `_TOOL_MODULES`
5. **CLI 入口**（選）：在 `src/twmcp/cli.py` 加 `@app.command()`
6. **測試**：`tests/test_<name>.py`，至少 3 個邊界 case
7. **Skill 觸發詞**：必要時更新 `skills/tw-utils/SKILL.md` 的 description
8. **跑全套**：`pytest && ruff check src tests && ruff format --check src tests`

範例 — 加一個簡單 tool：

```python
# src/twmcp/tools/example.py
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from mcp.server.fastmcp import FastMCP

def my_logic(x: str) -> dict:
    """Pure function — no MCP dependency."""
    return {"result": x.upper()}

def register(mcp: "FastMCP") -> None:
    @mcp.tool()
    def my_tool(x: str) -> dict:
        """One-line description that Claude reads for invocation hint."""
        return my_logic(x)
```

## 已實作 vs 未實作 (v0.1 → v1.0)

### ✅ v0.1 已實作 (11 tools)
- `validate_taiwan_id_number`, `validate_tax_id_number`
- `generate_test_taiwan_id_tool`, `generate_test_tax_id_tool`
- `normalize_taiwan_address`, `align_legacy_county_tool`
- `roc_year_to_western_tool`, `western_year_to_roc_tool`
- `simplified_to_traditional_tool`, `traditional_to_simplified_tool`
- `format_chinese_numerals_tool`

### ⏳ v0.2 待補 (~26 tools)
- `address_to_postal_code` / `address_zh_to_en` / `address_en_to_zh` — pypinyin + 中華郵政 KML
- `is_taiwan_business_day` / `lookup_holidays` — data.gov.tw dataset 14718
- `lookup_mrt_line` — TDX OAuth2
- `lookup_bank_code` — FISC R1_MEMBER.csv (✅ 已 verify 公開可用)
- `lookup_government_agency_code` / `lookup_county_basic_info` / `lookup_administrative_district` / `list_districts_in_county`
- `validate_license_plate` / `validate_phone` / `validate_postal_code`
- `lookup_24_solar_terms` / `lookup_zodiac` / `lunar_to_solar` (套件 `lunar-python` 1.4.8)
- `lookup_company_by_tax_id` — MOEA Swagger API（注意 `$top<=1000` 限制）
- `current_time_in` / `duration_humanize`
- `extract_pdf_metadata` / `extract_pdf_pages` / `extract_pdf_text`
- `fetch_url_as_markdown` — trafilatura

完整 v0.2-v1.0 roadmap 見 `README.md`。

## 已驗證的政府公開資料端點 (Codex GPT-5.5 用 curl 200 驗證)

| Endpoint | 內容 | 更新頻率 |
|---|---|---|
| `https://www.post.gov.tw/post/download/TOWN_MOI.kml` | 中華郵政 行政區+郵遞 (含 TOWNNAME/TOWNENG/ZIPCODE/CENTERLONG/CENTERLAT) | 月 |
| `https://www.fisc.com.tw/TC/OPENDATA/R1_MEMBER.csv` | FISC 銀行代號 (含純網銀+郵政) | 月 |
| `https://stat.fsc.gov.tw/FSC_OAS3_RESTORE/api/CSV_EXPORT?TableID=B14` | FSC 金融機構基本資料 | 月 |
| `https://web.pcc.gov.tw/tps/openDataApi/atmOpenData?runType=2` | PCC 政府採購（JSON） | 季 |
| `https://data.gov.tw/api/v2/rest/dataset/{14718,7307,22197}` | data.gov.tw catalog（CKAN-like） | 視 dataset |
| `https://data.gcis.nat.gov.tw/resources/swagger/swagger.json` | MOEA 商工（`$top<=1000`, `$skip<=500000`） | 時 |
| `https://tdx.transportdata.tw/api-service/swagger` | TDX 捷運/運輸（需 OAuth2 註冊 client_id） | 即 |

## 重要法規 / 邊界

- **2026 起補班補假取消**（2025 立法修正）。`is_taiwan_business_day` 需分流 2024-2025 歷史 vs 2026+ 簡化
- **中華郵政英譯 SOAP API 需申請固定 IP**（白名單），改用 `pypinyin` + 規則自寫
- **MOEA 商工 API 即時查需白名單 IP**，改用月度全量 dump 建本地索引
- **身分證/統編 fixtures** 強制 `is_test: true` 標記，避免被誤用於 production

## 編碼慣例

- **Python 3.11+**（用 `from __future__ import annotations`, `|` union, `dict[str, X]`）
- **Type hints**：tool register wrapper 用 `Literal` 限制 enum 參數
- **Ruff**：line-length=100, select=`E,F,I,N,UP,B,SIM`，SIM108 用 ternary
- **每個 tool 純函式 + register wrapper 分離**：純函式可直接被 CLI/test import，不依賴 MCP
- **錯誤處理**：tool 回 `{"valid": False, "reason": "..."}` dict 而非 raise，讓 LLM 能讀懂並重試
- **License header**：不寫，靠 LICENSE 檔
- **註解**：只寫 WHY 不寫 WHAT。歷史/相容性註解 ok（如「2010 升格新北市」），實作註解少
- **i18n**：所有 docstring、user-facing string 用繁體中文；變數/函式名英文

## 設計決策（已採納外部 LLM 建議）

| 來源 | 建議 | 採納狀態 |
|---|---|---|
| Cursor Grok 4.3 | Python + FastMCP + SQLite FTS5 預建索引 | ✅ FastMCP；FTS5 v0.4 階段 |
| Codex GPT-5.5 | 預建索引 vs 即時查詢混合，PCC 走 XML notice index | ✅ 設計階段已確認 |
| Gemini 2.5 Pro | HTTP transport 綁 `127.0.0.1` 不是 `0.0.0.0` | ✅ `server.py` 已實作 |
| Gemini 3.1 Pro | uvx/pipx 隔離；platformdirs 跨平台快取 | ✅ `utils/paths.py` |
| Gemini 3.1 Pro | 37 tools schema 太大，合併成 10-15 高階入口 | ⏳ v0.2 設計時考慮（會 break SKILL.md 對應表） |

完整外部 LLM 分析存 `docs/gemini-{2.5,3.1}-pro*-packaging-analysis.md`。

## 不要做的事

- ❌ 不要把 tool 邏輯寫進 `register()` inner function（會難以 test/CLI 共用）
- ❌ 不要用 `print()` debug — 用 logging 或測試
- ❌ 不要在 production 程式碼裡用 `gen-id` 產的 ID 當真實 PII
- ❌ 不要 hardcode `~/.twmcp` 路徑 — 用 `twmcp.utils.paths`
- ❌ 不要在 MCP HTTP mode 預設綁 `0.0.0.0`（用 `TWMCP_HOST` 顯式覆寫）
- ❌ 不要加 telemetry/analytics SDK — 開源 + 本地 + 無追蹤是核心賣點
- ❌ 不要在沒實測 endpoint 200 的情況下加新 data source — 抓 curl 確認

## Commit conventions

依現有 4 commits 看到的 style：

- `feat:` 新功能
- `fix:` 修 bug
- `style:` 純格式（ruff fix）
- `docs:` 文件/分析存檔
- 含 `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` trailer
- HEREDOC 多行 commit message 含「為什麼」

## 啟動 twmcp MCP 的 Claude Code session

在這個 repo root：

```bash
cd ~/Documents/mine/twmcp
claude   # 第一次會問是否信任 .mcp.json，按同意
```

驗證：在 Claude 對話內輸入 `/mcp` 應看到 `twmcp` connected 含 11 個 tools。

## 相關資源

- README.md — 用戶面 install/使用文件
- `docs/gemini-2.5-pro-packaging-analysis.md` — Gemini 2.5 Pro 封裝分析 (383 行)
- `docs/gemini-3.1-pro-preview-packaging-analysis.md` — Gemini 3.1 Pro 分析 (196 行)
- `~/Documents/mine/twmcp-design.md` — 完整研究設計文件
- Upstream（功能對照）：https://hub.twinkleai.tw/
- MCP Python SDK：https://github.com/modelcontextprotocol/python-sdk
- Claude Code Plugin 文檔：https://code.claude.com/docs/en/plugin-marketplaces
