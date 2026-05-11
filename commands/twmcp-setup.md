---
description: 安裝 twmcp 並驗證 MCP server 正常啟動
---

# /twmcp-setup

執行以下步驟完成 twmcp 安裝與驗證：

## 1. 檢查 Python 環境

```bash
python3 --version  # >= 3.11
which pipx || python3 -m pip install --user pipx
```

## 2. 安裝 twmcp

```bash
pipx install twmcp
twmcp version
```

## 3. 註冊到 Claude Code MCP

```bash
claude mcp add --transport stdio twmcp twmcp serve
claude mcp list  # 應該看到 twmcp
```

## 4. 驗證

跑幾個 CLI 測試：

```bash
twmcp id A123456789
twmcp tax-id 12345678
twmcp addr-normalize "台北市信義路五段7號"
twmcp roc-to-year 114
twmcp num 12345 --upper  # 應該輸出「壹萬貳仟參佰肆拾伍」
```

## 5. 在 Claude Code 中試用

重啟 Claude Code 後，問 Claude：「驗證 A123456789 是不是合法身分證」
應該自動透過 `mcp__twmcp__validate_taiwan_id_number` tool 回答。

## 故障排除

- 如果 `claude mcp add` 失敗：手動編輯 `~/Library/Application Support/Claude/claude_desktop_config.json`，加入：
  ```json
  {
    "mcpServers": {
      "twmcp": { "command": "twmcp", "args": ["serve"] }
    }
  }
  ```
- 如果 `pipx` 安裝失敗：用 `pip install --user twmcp` 並確認 `~/.local/bin` 在 PATH
- 如果 import 錯誤：跑 `pipx upgrade twmcp` 或重新安裝
