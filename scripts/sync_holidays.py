"""同步政府行政機關辦公日曆表 (data.gov.tw dataset 14718).

來源：行政院人事行政總處
2026 起：彈性放假與補班補假已取消 (依 2025 修法)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.request import Request, urlopen


# 行政院人事行政總處資料集 14718
# 實際 download endpoint 由 data.gov.tw resources 取得
HOLIDAY_DATASET_URL = "https://data.gov.tw/api/v2/rest/dataset/14718"

OUTPUT = Path(__file__).resolve().parents[1] / "src" / "twmcp" / "data" / "holidays.json"


def fetch(url: str) -> bytes:
    req = Request(
        url,
        headers={"User-Agent": "twmcp-sync/0.1 (+https://github.com/iml1s/twmcp)"},
    )
    with urlopen(req, timeout=30) as resp:
        return resp.read()


def main() -> int:
    print(f"[sync_holidays] fetching {HOLIDAY_DATASET_URL} ...", file=sys.stderr)
    try:
        raw = fetch(HOLIDAY_DATASET_URL)
        meta = json.loads(raw)
    except Exception as e:
        print(f"[sync_holidays] FAILED: {e}", file=sys.stderr)
        return 1

    # 找出實際 CSV resource
    resources = meta.get("resources") or meta.get("data", {}).get("resources") or []
    if not resources:
        print("[sync_holidays] no resources found in dataset 14718", file=sys.stderr)
        return 1

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[sync_holidays] wrote {OUTPUT}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
