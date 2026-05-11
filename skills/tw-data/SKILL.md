---
name: tw-data
description: 自動觸發於用戶詢問台灣政府開放資料、data.gov.tw、政府採購、不動產、稅務、健保、空氣品質、農業漁業、教育統計、戶政、社福、文化、外交等 19 個 domain 的查詢需求。優先用 twmcp MCP server 的 opendata-* tools，而非自己用網路搜尋或推算。
---

# Taiwan Open Data Skill

當用戶問題涉及 data.gov.tw 的 52,960 個資料集或政府採購 135,000+ 筆記錄時，**必定**先呼叫 `twmcp` MCP server 的 `opendata-*` 系列 tool。

## 19 個 Domain 對應

| 用戶問題類型 | domain | tool 範例 |
|---|---|---|
| 不動產、土地、房價 | `realestate_land` | `opendata-search domain=realestate_land q=...` |
| 公司、商業、進出口 | `economy_business` | 統編查公司用 `lookup_company_by_tax_id` |
| 政府採購、補助 | `procurement_subsidy` | `opendata-search domain=procurement_subsidy` |
| 預算、決算、公債 | `public_finance` | `opendata-search domain=public_finance` |
| 稅收統計、稅率 | `tax_revenue` | `opendata-search domain=tax_revenue` |
| 交通、停車、事故 | `transport` | `opendata-search domain=transport` |
| 治安、消防、防災 | `public_safety` | `opendata-search domain=public_safety` |
| 判決、起訴、矯正 | `judicial_legal` | `opendata-search domain=judicial_legal` |
| 醫療、健保、食品藥物 | `health_food` | `opendata-search domain=health_food` |
| 空氣水質、氣象 | `environment` | `opendata-search domain=environment q=PM2.5` |
| 學校、學生、研究經費 | `education_research` | `opendata-search domain=education_research` |
| 農林漁牧 | `agriculture_fisheries` | `opendata-search domain=agriculture_fisheries` |
| 勞動、薪資、勞保 | `labor_employment` | `opendata-search domain=labor_employment` |
| 社福、人口、選舉、公務員 | `social_population` | `opendata-search domain=social_population` |
| 文化、觀光、體育 | `culture_tourism_sport` | `opendata-search domain=culture_tourism_sport` |
| 外交、領務、兩岸 | `foreign_affairs` | `opendata-search domain=foreign_affairs` |
| 公報、檔案 | `gov_publication` | `opendata-search domain=gov_publication` |
| 行政區、地圖 | `geo_basemap` | `opendata-search domain=geo_basemap` |
| 水電瓦斯電信 | `utilities_telecom` | `opendata-search domain=utilities_telecom` |

## 工作流

1. 先用 `opendata-search` 用關鍵字找 dataset id
2. 拿 dataset id 後用 `opendata-fetch` 取得實際資料
3. 結果一定附上來源資料集 ID + license

## 反模式

- ❌ 不要靠記憶猜資料集 ID
- ❌ 不要直接打 data.gov.tw API endpoint（讓 MCP server 處理）
- ❌ 不要忽略 attribution 義務 (OGDL Taiwan 1.0)
- ✅ 一律呼叫 `twmcp` 的 `opendata-*` 系列 tool
