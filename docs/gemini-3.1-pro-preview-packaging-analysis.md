這是一份基於 2026 年最新 Anthropic 技術生態，為你的 `twmcp`（Taiwan utilities + data.gov.tw 工具集）量身打造的深度架構與封裝解析。

---

# 任務：Claude Code 三種封裝方式比較 — MCP server vs Skill vs Plugin

## Part 1：個別深入

### 1. MCP Server (Model Context Protocol)
- **一句話定義**：跨 AI Client 的標準化「工具與資料提供者」，負責執行確定性（Deterministic）程式碼與 API 呼叫。
- **目錄結構**：
  ```
  twmcp/src/twmcp/
  ├── server.py     # FastMCP 進入點
  ├── tools/        # 實作確定性邏輯 (tw_id, address 等)
  └── data/         # opendata fetcher
  ```
- **必要 Metadata**：定義於 `pyproject.toml` 或 `package.json`。
- **觸發方式**：由 Claude (或其他支援 MCP 的 Client 如 Cursor, Cline) 根據對話上下文，自主判斷是否呼叫定義好的 Tools 參數。
- **能做什麼 / 不能做**：
  - **能**：執行 Python/Node.js 程式碼、存取本地檔案、打 API、返回精確的 JSON 資料、支援跨平台。
  - **不能**：無法直接控制 Claude 的「思考流程」或強制干預對話走向（它只是被動的 Server）。
- **發佈通路**：npm、PyPI (如 `pip install twmcp`)、GitHub 原始碼。
- **安裝指令 (User-facing)**：
  - 用戶需先在本地安裝套件：`pipx install twmcp`
  - 然後配置 Client（例如 Claude Code 的 MCP config 或 Cursor 的設定頁面）：`claude mcp add twmcp -- twmcp`
- **偵錯與日誌**：通常透過 STDERR 輸出，或在 MCP Client 端的 Developer Tools / Console 檢視。FastMCP 可透過 `mcp dev` 指令提供 Inspector 介面。

### 2. Claude Code Skill
- **一句話定義**：特定於 Claude Code 的「軟性工作流與 Prompt 注入器」，教導 LLM 在遇到特定情境時該怎麼思考與行動。
- **目錄結構**：
  ```
  ~/.claude/skills/tw-data/
  └── SKILL.md      # 包含 YAML frontmatter 與 Markdown 說明
  ```
- **必要 Metadata**：Markdown 頂部的 YAML Frontmatter（包含 `name`, `description` 等）。
- **觸發方式**：
  - **自動 invoke**：當用戶的問題命中 `description` 裡的關鍵字時，Claude Code 會將整份 `SKILL.md` 載入 Context。
  - **手動指令**：用戶明確提及「使用 tw-data skill」或透過 `/skill` 呼叫。
- **能做什麼 / 不能做**：
  - **能**：規範 LLM 的思考模式（例如：「遇到統編，不要自己瞎猜，**必須**呼叫 MCP tool `lookup_company`」）。
  - **不能**：不能執行真正的 Code，不能直接發送網路請求（必須依賴 MCP 或內建工具代勞）。
- **發佈通路**：GitHub Repo（用戶手動 Clone 或 Symlink），或透過 Plugin 系統打包。
- **安裝指令 (User-facing)**：通常是複製檔案 `cp -r skills/tw-data ~/.claude/skills/`，或建立軟連結。
- **偵錯與日誌**：觀察 Claude 的回覆是否出現 `<activated_skill>` tag，如果沒有觸發，代表 `description` 關鍵字（Model Decay）設計不佳。

### 3. Claude Code Plugin (2025 年導入)
- **一句話定義**：Claude Code 專屬的「一鍵安裝包套件系統」，可將 MCP, Skills, Commands, Agents, Hooks 綑綁成一個完整的擴充模組。
- **目錄結構**：
  ```
  twmcp/
  ├── .claude-plugin/
  │   └── plugin.json   # Plugin Manifest
  ├── agents/           # 特化 Agent
  ├── commands/         # 自訂斜線指令 (如 /twmcp-setup)
  └── skills/           # 綁定的 Skills
  ```
- **必要 Metadata**：`.claude-plugin/plugin.json`，需宣告 entrypoints 與綁定的資源。
- **觸發方式**：Plugin 本身是容器，實際觸發的是其內部包含的 Command（用戶輸入 `/twmcp-refresh`）或 Skill（自動觸發）。
- **能做什麼 / 不能做**：
  - **能**：極大化降低使用者的 Onboarding 成本，統管生命週期，注入環境變數。
  - **不能**：無法脫離 Claude Code 環境使用（Cursor/Cline 不認得 `.claude-plugin`）。
- **發佈通路**：Claude Code Marketplace，或指定 Git URL 安裝。
- **安裝指令 (User-facing)**：`claude plugin install iml1s/twmcp`。
- **偵錯與日誌**：`claude plugin logs twmcp` 或透過 Claude Code 的 Debug 模式檢視 Plugin 生命週期。

---

## Part 2：四維比較矩陣

| 維度 | MCP server | Skill (`SKILL.md`) | Plugin (`plugin.json`) |
|---|---|---|---|
| **跨 client 通用？** | ✅ 是 (Cursor, Cline, Claude, etc.) | ❌ 否 (僅限 Claude Code) | ❌ 否 (僅限 Claude Code) |
| **需要 Client 重啟？** | ⚠️ 視 Client 實作 (通常需 Reload) | ❌ 否 (即時讀取目錄) | ⚠️ 是/否 (依賴安裝後自動熱載) |
| **可內含確定性 Code？** | ✅ 是 (Python/JS) | ❌ 否 (純 Text/Prompt) | ✅ 透過包含 MCP 實現 |
| **可內含 LLM-driven workflow？**| ❌ 否 (僅回傳 Tool 執行結果) | ✅ 是 (定義思考鏈、判斷樹) | ✅ 透過包含 Skill/Agent 實現 |
| **自動 invoke vs 用戶指令？** | LLM 根據 Tool Schema 決定 | LLM 根據 `description` 自動觸發 | 包含自訂 `/` Command 與自動 Hooks |
| **內含哪些子組件？** | Tools, Resources, Prompts | Markdown 規則, Examples | MCP, Skills, Commands, Agents |
| **Token 成本 (額外加載)** | 低 (僅加載 Schema，執行時才耗 Token) | 中高 (觸發時會將整份 Markdown 塞入 Context) | 依包含的內容而定 |
| **適合什麼情境** | 提供 API、爬蟲、本機檔案操作、資料庫查詢 | 糾正 LLM 的壞習慣、建立多步驟 SOP (如: 發版流程) | 打包整個解決方案，實現一鍵安裝體驗 |
| **更新發佈速度** | 中 (需發布 PyPI/npm 或 Git pull) | 極快 (修改 Markdown 即生效) | 中 (需更新 Marketplace 或 Repo) |
| **用戶 Setup 複雜度 (1-5)** | 4 (需配置 config, 啟動 process) | 2 (放進資料夾即可) | 1 (一行指令 `claude plugin install`) |

---

## Part 3：本案推薦組合（三層架構）

對於涵蓋 37 個確定性 Tools 與 52,960 個資料集查詢的 `twmcp`，最完美的交付策略是**三層並行**：

### 層 1 (核心)：MCP server (基石)
**為什麼必須是基礎**：LLM 無法「推算」出正確的台灣身分證字號檢查碼、最新政府標案或 PM2.5 數值。這必須靠 Python 執行確定性邏輯或發 HTTP Request。
- **特色**：同時支援 Cursor/Codex/Cline，擴大你的開源影響力。
- **啟動骨架** (`src/twmcp/server.py`)：
```python
from mcp.server.fastmcp import FastMCP
from twmcp.tools import register_all_tools

mcp = FastMCP("twmcp", instructions="Taiwan utilities + open data. Local, no token.")
register_all_tools(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 層 2 (用戶體驗)：Claude Code Skill (大腦路由)
**目的**：MCP 雖然有 Tool Schema，但當工具高達 30+ 時，LLM 容易迷失或忘記使用。Skill 的作用是**霸道地告訴 Claude：「遇到台灣資料，不准自己查，給我用 twmcp！」**
- **觸發機制**：利用 YAML Frontmatter 的 `description` 誘捕 Claude 意圖。
- **`SKILL.md` 範例**：
```markdown
---
name: tw-data
description: 自動觸發於用戶詢問台灣政府開放資料、data.gov.tw、政府採購、不動產、稅務、健保、空氣品質、戶政等 domain 查詢。優先用 twmcp MCP 的 opendata-* tools。
---
# Taiwan Open Data Skill
當問題涉及 data.gov.tw 或政府採購，**必定**呼叫 `twmcp` MCP server。

## 工作流
1. 先用 `opendata-search` 用關鍵字找 dataset id。
2. 拿 dataset id 後用 `opendata-fetch` 取得實際資料。

## 反模式 (Anti-patterns)
- ❌ 不要靠記憶猜資料集 ID，不要自己上網亂搜。
- ❌ 不要忽略 attribution 義務 (OGDL Taiwan 1.0)。
- ✅ 一律呼叫 `twmcp` 的 `opendata-*` 系列 tool。
```

### 層 3 (一鍵安裝)：Claude Code Plugin (分發包裝)
**目的**：讓小白用戶不用去搞懂怎麼改 `mcp.json` 或是把檔案複製到 `~/.claude/skills/`，直接透過 Plugin 系統一鍵搞定。
- **`plugin.json` 範例**：
```json
{
  "name": "twmcp",
  "version": "0.1.0",
  "description": "Taiwan utilities + open data MCP — open-source, local, no token.",
  "components": {
    "mcp_servers": {
      "twmcp": {
        "command": "uvx",
        "args": ["twmcp"]
      }
    },
    "skills": ["skills/tw-utils", "skills/tw-data"],
    "commands": ["commands/twmcp-setup.md", "commands/twmcp-refresh.md"],
    "agents": ["agents/tw-data-analyst.md"]
  }
}
```

---

## Part 4：實際 File Tree 職責清單

結合你提供的專案目錄，這是一個完美的 2026 現代化 Claude 擴充專案結構：

```text
twmcp/
├── .claude-plugin/
│   └── plugin.json         # [Plugin] 總入口 Manifest，定義 MCP/Skills 綁定
├── agents/
│   └── tw-data-analyst.md  # [Plugin-Agent] 專門處理複雜交叉比對的 Sub-agent
├── commands/
│   ├── twmcp-setup.md      # [Plugin-Cmd] 提供給用戶的 /twmcp-setup 自訂指令
│   └── twmcp-refresh.md    # [Plugin-Cmd] 重新載入 open data 索引的指令
├── skills/
│   ├── tw-data/SKILL.md    # [Skill] 攔截「開放資料」意圖的 Workflow 規則
│   └── tw-utils/SKILL.md   # [Skill] 攔截「身分證/統編/地址」意圖的 Workflow 規則
├── src/twmcp/
│   ├── server.py           # [MCP] FastMCP 伺服器進入點 (處理 stdio/http transport)
│   ├── cli.py              # [MCP] 提供 pipx 安裝後可直接執行的 CLI 介面
│   ├── tools/
│   │   ├── address.py      # [MCP-Tool] 台灣地址正規化與郵遞區號邏輯
│   │   ├── tw_id.py        # [MCP-Tool] 台灣身分證/居留證驗證產生邏輯
│   │   └── calendar_roc.py # [MCP-Tool] 民國紀年與農曆轉換邏輯
│   └── data/               # [MCP-Data] 負責串接 data.gov.tw 的核心邏輯
├── pyproject.toml          # Python 套件定義，指定依賴 (hatchling, mcp, lunar-python 等)
└── README.md               # 用戶手冊，包含跨 Client (Cursor/Claude) 的安裝指引
```

---

## Part 5：陷阱與最佳實踐

1. **Skill Model Decay (技能失憶症)**：
   Claude 在面對長對話時，可能不會每次都重新載入 Skill。**最佳實踐**：在 `SKILL.md` 的 `description` 中埋入極度高頻的長尾關鍵字（如 `data.gov.tw`, `統編`, `身分證`, `健保`），讓系統引擎面的 Semantic Router 能精準命中並將 Skill 拉回 Context。
2. **MCP Transport 選擇 (Stdio vs HTTP)**：
   預設應強制使用 `stdio`。這是因為在開發者機器的本地環境，HTTP Port (如 `8765`) 極易衝突，且有潛在的本地權限裸奔風險（SSRF）。若必須用 HTTP (如 `server.py` 裡的 `streamable-http`)，務必綁定 `127.0.0.1` 而非 `0.0.0.0`。
3. **隔離依賴環境 (uvx / pipx)**：
   不要讓用戶用 `pip install twmcp` 污染全局 Python 環境。在 Plugin 配置或 README 中，**強制推薦使用 `uvx twmcp` 或 `pipx run twmcp`**，確保 Python 依賴（如 `lunar-python`, `opencc-python-reimplemented`）沙盒化運行。
4. **Tool Schema 爆炸導致 Token 消耗**：
   你有 37 個 deterministic tools，這會導致每次 MCP Handshake 傳給 LLM 的 Schema 非常巨大。**最佳實踐**：盡量合併同質性 Tool（例如把 `validate_tw_id`, `generate_tw_id` 合併為一個 `handle_tw_id(action="validate|generate")`），將 37 個 Tool 濃縮到 10-15 個高階入口。
5. **資料來源與 License 標示 (Attribution)**：
   開放資料平台強制要求標示來源 (OGDL Taiwan 1.0)。必須在 MCP Tool 的 Return string 中，強制 append 資料來源網址與授權宣告，不要指望 LLM 會「記得」幫你寫上去。
6. **跨平台路徑與快取 (Pathing & Cache)**：
   5萬多筆 open data index 不可能每次 Fetch。當你的 Python Code 寫快取時，不要硬寫 `~/.twmcp`，請使用標準的 `platformdirs` 套件處理 macOS (`~/Library/Caches/`)、Windows (`%LOCALAPPDATA%`) 和 Linux (`~/.cache/`) 的路徑問題。
7. **Telemetry 隱私紅線**：
   身為取代閉源商業系統（`hub.twinkleai.tw`）的開源方案，你的賣點是「Local, no token, no telemetry」。請確保你的 Python 代碼中**絕對不包含任何追蹤 SDK (如 PostHog / Sentry)**，這在企業級開發者社群中是絕對的踩雷紅線。
