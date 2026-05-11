# twmcp

> Taiwan utilities + open-data MCP server — **open-source, local, no token, no rate limit**.
> Drop-in alternative to [hub.twinkleai.tw](https://hub.twinkleai.tw/).

## 為什麼？

Twinkle Hub 是一個閉源 SaaS MCP proxy，每個 query 都要經過他們 server、用 `sk-...` token 計費、未來會收費。
所有 37 個工具的演算法都已標 MIT，所有資料都是政府公開資料。**沒有理由把資料主權交出去**。

twmcp 是同等功能的開源、本地、永久免費替代品：
- 跨所有 MCP client (Claude Desktop / Cursor / Continue / Cline / Claude Code)
- 也是 Claude Code Skill + Plugin
- 完整 CLI（不用 LLM 也可直接終端機呼叫）

## 安裝

### 方法 A：MCP server（所有 client 通用）

推薦用 `uvx` 或 `pipx` 隔離依賴環境，避免污染全域 Python：

```bash
# 選項 1: uvx 隨用隨開（最輕量）
uvx twmcp serve

# 選項 2: pipx 安裝後常駐 PATH
pipx install twmcp
twmcp serve

# Claude Desktop / Claude Code（任一安裝方式後）
claude mcp add --transport stdio twmcp twmcp serve
# 或用 uvx
claude mcp add --transport stdio twmcp -- uvx twmcp serve

# Cursor (~/.cursor/mcp.json)
# { "mcpServers": { "twmcp": { "command": "uvx", "args": ["twmcp", "serve"] } } }
```

### 方法 B：Claude Code Plugin（一鍵安裝）

```bash
/plugin install iml1s/twmcp
```

### 方法 C：直接 CLI 使用（無 LLM）

```bash
twmcp id A123456789
twmcp tax-id 12345678
twmcp addr-normalize "台北市信義路五段7號"
twmcp roc-to-year 114
```

## 工具一覽

### TW-specific (23)
身分證/統編 (驗證+生成 test fixture)、地址正規化、郵遞區號 (3/5/6 碼)、行政區查詢、22 縣市基本資料、政府機關代碼、金融機構代號、四大捷運站線、車牌、電話、ROC↔西元、商業日、國定假日、舊縣名對齊。

### Generic / CJK-shared (14)
IANA 時區當下時間、秒數人類化、PDF 三件套 (metadata/pages/text)、URL→markdown、阿拉伯↔中文數字、24 節氣、生肖、農曆↔國曆、簡↔繁。

完整 schema 與範例：見 `docs/tool-reference.md`。

## 資料來源 (公開, OGDL Taiwan 1.0 + 各原始 license)

- [data.gov.tw](https://data.gov.tw/) — 52,960 datasets
- [中華郵政 TOWN_MOI.kml](https://www.post.gov.tw/post/download/TOWN_MOI.kml) — 郵遞區號 + 行政區
- [行政院人事行政總處辦公日曆](https://data.gov.tw/dataset/14718) (含 2024-2025 補班；2026+ 簡化)
- [FISC 銀行代號](https://www.fisc.com.tw/TC/OPENDATA/R1_MEMBER.csv)
- [FSC 金融機構](https://stat.fsc.gov.tw/FSC_OAS3_RESTORE/api/CSV_EXPORT?TableID=B14)
- [MOEA 商工資料](https://data.gcis.nat.gov.tw/) — 統編查公司
- [TDX](https://tdx.transportdata.tw/) — 捷運站線
- [PCC 政府電子採購網](https://web.pcc.gov.tw/) — 採購資料

## 隱私

- 所有計算在本地，無外部 API 呼叫（除少數 daily-refreshed 資料）
- 無 token、無使用追蹤、無 telemetry
- 身分證/統編 fixtures 強制標記 `is_test: true`

## License

- 程式碼：MIT
- 資料：OGDL Taiwan 1.0 passthrough + 各 dataset 原始 license

## Roadmap

| 版本 | 範圍 |
|---|---|
| v0.1 MVP | 22 個純函式 tools (本 commit) |
| v0.2 | 商業日 + 假日 + 捷運 + 銀行 + 機關 |
| v0.3 | MOEA 公司本地索引 + 地址中英譯 |
| v0.4 | data.gov.tw FTS5 catalog 索引 |
| v0.5 | PCC 採購 daily sync |
| v0.6 | Claude Code plugin marketplace 上架 |
| v1.0 | 完整 19 domains + Web UI |
