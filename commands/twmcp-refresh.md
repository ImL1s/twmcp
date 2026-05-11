---
description: 重新建立 twmcp 本地索引 (data.gov.tw catalog + 政府採購 + 假日)
---

# /twmcp-refresh

執行本地索引重建。在以下情境使用：
- 第一次安裝後
- 政府資料公布大量更新（如年初新版假日）
- 索引檔損毀

## 執行

```bash
# 重建所有索引 (預計 5-15 分鐘)
twmcp refresh --all

# 或選擇性重建
twmcp refresh --holidays      # 國定假日（年更）
twmcp refresh --districts     # 行政區 (TOWN_MOI.kml, 月更)
twmcp refresh --banks         # FISC R1_MEMBER.csv
twmcp refresh --catalog       # data.gov.tw 全量 catalog (慢)
twmcp refresh --pcc           # 政府採購（每日）
```

## 來源說明

| 索引 | 來源 | 更新頻率 |
|---|---|---|
| 假日 | data.gov.tw dataset 14718 | 年 |
| 行政區 | post.gov.tw TOWN_MOI.kml | 月 |
| 銀行代號 | fisc.com.tw OPENDATA/R1_MEMBER.csv | 月 |
| 機關代碼 | data.gov.tw dataset 7307 | 週 |
| 採購 | web.pcc.gov.tw notice index | 日 |
| catalog | data.gov.tw/datasets/export/json | 週 |

## 故障排除

- 政府網站偶有 5xx → 自動重試 3 次，最終失敗會 keep 舊版索引
- TDX 需要 API key（建議到 https://tdx.transportdata.tw/ 註冊）
- 索引位置：`~/.twmcp/cache/`（可用 `--cache-dir` 自訂）
