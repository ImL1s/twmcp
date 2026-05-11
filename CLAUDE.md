# twmcp — Claude Code 工作指南

> Taiwan utilities + open-data MCP server. Drop-in 開源替代品 for [hub.twinkleai.tw](https://hub.twinkleai.tw/).
> 程式 MIT、資料 OGDL Taiwan 1.0。本地、無 token、無限流。

## 專案緣起與目的

### 為什麼存在

對標 [hub.twinkleai.tw](https://hub.twinkleai.tw/) — 一個閉源 SaaS MCP proxy，把 37 個 deterministic 台灣工具
（身分證/統編 checksum、地址正規化、農曆等）+ data.gov.tw 52,960 個資料集 + 政府採購 135,000+ 筆，
打包成單一 `https://api.twinkleai.tw/mcp/` 端點，用 `sk-...` Bearer token 計費。

### 我們解掉的痛點

| Twinkle Hub 限制 | twmcp 解法 |
|---|---|
| 需要 `sk-...` Bearer token，新帳號 0 餘額 | 完全本地，無 token |
| Alpha 期免費，將來 pay-as-you-go + Starter/Pro 訂閱 | 永久免費（程式 MIT、資料 OGDL Taiwan 1.0） |
| 所有 query 經他們 server (即使他們宣稱 zero storage) | 純本地計算，無外部呼叫（除少數 daily-refreshed 資料） |
| SPOF：他們 server 掛了你就沒得用 | 本地 SQLite + pip/uvx 安裝 |
| Pro tier 才有 99.5% SLA | 自己跑就是 100% SLA |
| 鎖定 Claude/Cursor 等特定 client 透過 `.json` 設定 | MCP + Skill + Plugin + CLI 四層交付，任何 MCP client 都能用 |
| 隱私：使用模式經第三方 | 無 telemetry、無追蹤、無分析 SDK |

### 為什麼合法 / 為什麼可重做

1. **Twinkle Hub 自己把每個 tool 標 MIT license**（見 hub.twinkleai.tw/en/tools 每個 tool 卡片）
2. **資料全為政府開放資料** (OGDL Taiwan 1.0 + 各機關開放授權)
3. **Twinkle Hub 官方在 pricing 頁親自說**：
   > "Twinkle Hub is an MCP endpoint, not an SDK ... MCP is open protocol;
   > **rolling your own or going elsewhere is always an option**."

   等於官方明示鼓勵自製。
4. **演算法都是公開標準**：身分證 checksum（內政部公開）、統編 mod-5/mod-10（財政部公告）、
   Hanyu Pinyin（中華郵政公開規則）、農曆（lunar-python 套件實作天文演算法）
5. **名稱避開商標**：`twmcp`，不是 `twinkle-*`

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
pytest tests/test_tw_id.py::TestTaiwanID                              # 跑單個 class
pytest tests/test_tw_id.py::TestTaiwanID::test_valid_national_male    # 跑單個 test
pytest -k "TaxID"           # 名稱/class 含 TaxID 的所有 test（-k 大小寫不敏感）
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
- **Tests**：class-based grouping (`TestTaiwanID`、`TestTaxID`、`TestForeignerID`...) — 一個 class 對應一個邏輯區塊（純函式 / 邊界 / 規則分支），不是按 fixture 拆檔

## 環境變數

純函式 tool 不需任何環境變數。下表是 server / CLI / paths 層的覆寫旋鈕：

| 變數 | 預設 | 用途 |
|---|---|---|
| `TWMCP_TRANSPORT` | `stdio` | MCP transport (`stdio` 給 Claude Code/Cursor、`http` 給遠端) |
| `TWMCP_HOST` | `127.0.0.1` | HTTP mode 綁定 host — **絕不**改成 `0.0.0.0` 除非前面有 auth gateway |
| `TWMCP_PORT` | `8765` | HTTP mode 埠 |
| `TWMCP_CACHE_DIR` | `platformdirs.user_cache_dir("twmcp")` | 覆寫 cache 目錄；接受 `~` 展開 |
| `TWMCP_CONFIG_DIR` | `platformdirs.user_config_dir("twmcp")` | 覆寫 config 目錄；接受 `~` 展開 |
| `TWMCP_DATA_DIR` | `platformdirs.user_data_dir("twmcp")` | 覆寫 data 目錄（下載的 open data index）；接受 `~` 展開 |

新加 path 旋鈕一律走 `src/twmcp/utils/paths.py`，不要 hardcode `~/.twmcp`。

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

## CI 與每日資料更新

兩條 GitHub Actions workflows（`.github/workflows/`）：

- **`ci.yml`** — push/PR 觸發；Python `3.11 / 3.12 / 3.13` 三版矩陣；流程：`pip install -e ".[dev]"` → `ruff check` → `ruff format --check` → `pytest -q` → CLI smoke (`twmcp version`、`twmcp id A123456789`、`twmcp roc-to-year 114`、`twmcp addr-normalize "台北市信義路5段7號"`)。**改 deps 前先在這三版本上跑過**。
- **`daily-refresh.yml`** — cron `0 20 * * *` (UTC，等於 TW 04:00) + manual dispatch；跑 `scripts/sync_holidays.py` 與 `scripts/sync_pcc.py --since yesterday`（`continue-on-error: true` 不擋整個 workflow），有 diff 就以 `github-actions[bot]` commit 到 `src/twmcp/data/` 並 push。

新加 daily sync script 規則：放 `scripts/sync_*.py`，輸出寫進 `src/twmcp/data/`（會被 commit），並在 `daily-refresh.yml` 多一行 `python scripts/sync_<your>.py`。執行端只用 stdlib（`urllib.request` + `json`），避免拖入額外 deps；端點需先實際 `curl` 200 驗證才能加。

## 啟動 twmcp MCP 的 Claude Code session

在這個 repo root：

```bash
cd ~/Documents/mine/twmcp
claude   # 第一次會問是否信任 .mcp.json，按同意
```

驗證：在 Claude 對話內輸入 `/mcp` 應看到 `twmcp` connected 含 11 個 tools。

## 研究編組與貢獻 (Multi-AI Provenance)

這個專案不是單一 LLM 產出。設計過程動員 5 個 AI + 1 個 web scraping 工具編組，
每個 LLM 從不同角度切入，互相驗證 + 互補盲點。完整輸出都存進 `docs/` 與 `~/Documents/mine/twmcp-design.md`。

| LLM / 工具 | 角色 | 主要貢獻 | 完整輸出 |
|---|---|---|---|
| **Claude Opus 4.7** (1M context) | 統籌 + 實作 | BrightData 抓取、最終整合、實際建 repo、跑測試、git commit、所有採納決策 | 本對話 + commits |
| **Cursor Grok 4.3** (1M context) | 反推架構師 | Twinkle Hub stack 推測為 Python+Starlette+PostgreSQL+Redis；7 大架構決策（語言/transport/資料層/註冊/設定/部署/測試）；5 個重點難關（農曆/商業日/data.gov.tw schema/PCC sync/地址邊界） | 本對話 |
| **Codex GPT-5.5** (reasoning_effort=xhigh) | 套件考古學家 | 37 tools → PyPI 套件映射表；用 curl 實測 4 個政府公開 endpoint（200/302/401 驗證）；完整 ID+統編 checksum 實作 (源於這個輸出)；34 個 unit test 邊界 case；MOEA Swagger `$top<=1000` 限制發現 | 本對話 |
| **Gemini 2.5 Pro** (gemini CLI) | 封裝設計師 | 完整 FastAPI server 骨架；10 維 MCP/Skill/Plugin 比較矩陣；7 個陷阱 + best practice；HTTP transport 安全 binding `127.0.0.1`（已採納 server.py） | `docs/gemini-2.5-pro-packaging-analysis.md` (383 行) |
| **Gemini 3.1 Pro Preview** (gemini -m gemini-3.1-pro-preview) | 工程顧問 | uvx/pipx 隔離建議（已採納 README + .mcp.json）；platformdirs 跨平台快取（已採納 utils/paths.py）；Tool Schema 爆炸警告建議合併 37→10-15 高階入口（v0.2 考慮）；絕對不包含 telemetry SDK 紅線 | `docs/gemini-3.1-pro-preview-packaging-analysis.md` (196 行) |
| **BrightData MCP** | SPA 深抓 | hub.twinkleai.tw 完整 6 個子頁面抓取（en/tools, en/data, en/docs, en/mcp, en/pricing, en/faq）— WebFetch 抓不到的 SPA 內容 | (即時) |

### Gemini 版本踩坑記錄（防止下次重蹈覆轍）

- `gemini -p` 預設使用 **Gemini Flash 等級**，不是 Pro
- `gemini-3-pro` / `gemini-3-pro-latest` / `gemini-2.5-pro-preview` → **404 不存在**
- `gemini-3-pro-preview` / `gemini-3.1-pro-preview` → 能跑，但**模型自報 "gemini-2.5-pro"**（LLM 自我認知偏差，**不是 alias**）
- `gemini-2.5-pro` → 穩定可用（也是當前在這台 OAuth personal 帳號下實質最強的 stable model）
- **正確用法**：`gemini -m gemini-3.1-pro-preview -p "..." --approval-mode yolo`

### 多 LLM 互相驗證的共識點

- ✅ 三方都建議 Python + FastMCP（與目前 server.py 一致）
- ✅ 三方都建議「預先索引 vs 即時查詢」走前者（v0.2 設計階段照辦）
- ✅ 三方都建議「stdio 預設、HTTP 為輔，HTTP 必須綁 127.0.0.1」
- ✅ 三方都建議三層交付（MCP + Skill + Plugin）不互斥

## 關鍵發現（研究階段挖出來的重要事實）

1. **Twinkle Hub 沒有公開 source code** — GitHub `ai-twinkle/Hub` repo 只是 community feedback，整個 ai-twinkle org 16 個 repo 都沒 hub 後端
2. **8 個 connectors 全為公開既有 MCP**（Playwright, Chrome DevTools, n8n, Notion, Sentry, Google, Sequential Thinking, Context7）— Twinkle Hub 只是「教你怎麼裝」
3. **opendata-* tools 只有 5 個**（不是 37）— 37 是 utility tools 數量
4. **2026 起補班補假已取消**（2025 修法），歷史日曆 (2024-2025) 與未來規則需分流
5. **中華郵政英譯 SOAP API 需固定 IP 白名單** → 用 pypinyin + 規則自寫
6. **MOEA 商工 API 即時查需固定 IP 白名單** + `$top<=1000` `$skip<=500000` 限制 → 用月度 dump 建本地索引
7. **PCC 採購不是乾淨 JSON API** — 走 notice index `prkms/tender/common/noticeDate/readTenderNoticeDate`，逐 XML 下載 upsert，需限速 1 req/s + sha256 manifest
8. **MOEA `validate_taiwan_id_number` 認 `[A-Z][89][0-9]{8}` 為 2021+ 新式外來人口** — Twinkle Hub 同此規則
9. **OpenCC `s2tw` 預設輸出**「叄」(三的大寫繁體變體)，非「參」— 細節由字典決定
10. **FastMCP `mcp.settings.host`/`port`** 可在 `mcp.run()` 之前覆寫 — 用於安全 binding

## 相關資源

### 內部文件

- `README.md` — 用戶面 install/使用文件
- `docs/gemini-2.5-pro-packaging-analysis.md` — Gemini 2.5 Pro 完整封裝分析 (383 行)
- `docs/gemini-3.1-pro-preview-packaging-analysis.md` — Gemini 3.1 Pro 完整分析 (196 行)
- `~/Documents/mine/twmcp-design.md` — Claude Opus 4.7 統整的完整研究設計文件
- `.claude-plugin/plugin.json` — Claude Code plugin manifest
- `.mcp.json` — MCP server 自動載入設定（local venv binary）

### Upstream（功能對照）

- https://hub.twinkleai.tw/ — Twinkle Hub 主站
- https://hub.twinkleai.tw/en/tools — 37 utility tools 完整清單 + schema
- https://hub.twinkleai.tw/en/data — 19 domains data.gov.tw 分類
- https://hub.twinkleai.tw/en/docs — 安裝指南
- https://hub.twinkleai.tw/en/pricing — pricing 頁（含「rolling your own」聲明）
- https://github.com/ai-twinkle/Hub — community feedback only repo (78 stars)
- https://github.com/ai-twinkle — Twinkle AI org（16 個 repo，無後端 source）

### MCP / Claude Code 框架

- https://github.com/modelcontextprotocol/python-sdk — MCP Python SDK
- https://github.com/modelcontextprotocol/specification — MCP 協議規格
- https://code.claude.com/docs/en/plugin-marketplaces — Claude Code Plugin Marketplaces
- https://github.com/anthropics/claude-plugins-official — 官方 plugins 倉庫（v0.6 上架目標）

### 政府公開資料端點（Codex curl 200 已驗證）

- https://www.post.gov.tw/post/download/TOWN_MOI.kml — 中華郵政行政區 + 郵遞
- https://www.fisc.com.tw/TC/OPENDATA/R1_MEMBER.csv — FISC 銀行代號（含純網銀+郵政）
- https://stat.fsc.gov.tw/FSC_OAS3_RESTORE/api/CSV_EXPORT?TableID=B14 — FSC 金融機構基本資料
- https://web.pcc.gov.tw/tps/openDataApi/atmOpenData?runType=2 — PCC 政府採購（JSON）
- https://data.gov.tw/api/v2/rest/dataset/14718 — 行政機關辦公日曆表 (人事行政總處)
- https://data.gov.tw/api/v2/rest/dataset/7307 — 政府機關代碼
- https://data.gov.tw/api/v2/rest/dataset/22197 — 公司登記基本資料
- https://data.gcis.nat.gov.tw/resources/swagger/swagger.json — MOEA 商工 OAS 規格
- https://tdx.transportdata.tw/api-service/swagger — TDX 運輸資料（含四大捷運，需 OAuth2）
- https://github.com/ruyut/TaiwanCalendar — 社群版 JSON 日曆 fallback

### 開源套件依賴（已查證 2026-05 PyPI 最新版）

- `lunar-python` 1.4.8 / `lunardate` 0.2.2 — 農曆 + 節氣
- `python-stdnum` 2.2 — 國際 ID 標準（含 TW ID）
- `taiwanid` 0.2.0 — 台灣身分證
- `phonenumbers` 9.0.30 — Google libphonenumber port
- `cn2an` 0.5.24 — 中文/阿拉伯數字
- `opencc-python-reimplemented` 0.1.7 — 簡繁轉換
- `PyMuPDF` 1.27.2.3 / `pdfplumber` 0.11.9 / `pypdf` 6.11.0 — PDF
- `trafilatura` 2.0.0 — URL → markdown
- `pypinyin` 0.55.0 — 漢語拼音
- `holidays` 0.96 / `chinese-calendar` 1.11.0 — 國際/中國假日
- `platformdirs` >=4,<5 — 跨平台快取路徑
- `Babel` 2.18.0 — 國際化（duration humanize）

## 法律與授權

- **程式碼**：MIT（與 Twinkle Hub 各 tool 宣告一致）
- **資料**：OGDL Taiwan 1.0 passthrough + 各 dataset 原始 license
- **命名**：`twmcp` 避開 Twinkle 商標
- **描述**：「open-source alternative to」「drop-in replacement」，不寫「clone」「fork」「rip-off」
- **每個 dataset 回應必附 attribution**：來源 URL + 機關名 + license
- **身分證/統編 fixtures 強制 `is_test: true` 標記** — 避免被誤用為真實 PII
