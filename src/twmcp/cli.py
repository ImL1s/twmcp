"""twmcp CLI — terminal 直接呼叫每個工具或啟動 MCP server."""

from __future__ import annotations

import json
import os
import sys

import typer

from twmcp.tools.address import align_legacy_county, normalize_address
from twmcp.tools.calendar_roc import roc_to_western, western_to_roc
from twmcp.tools.chinese import (
    format_chinese_numerals,
    simplified_to_traditional,
    traditional_to_simplified,
)
from twmcp.tools.tw_id import (
    generate_test_tax_id,
    generate_test_taiwan_id,
    validate_tax_id,
    validate_taiwan_id,
)

app = typer.Typer(
    name="twmcp",
    help="Taiwan utilities + open data MCP — CLI + server. Open-source, local, no token.",
    no_args_is_help=True,
    add_completion=False,
)


def _dump(obj) -> None:
    typer.echo(json.dumps(obj, ensure_ascii=False, indent=2))


@app.command()
def serve(transport: str = typer.Option("stdio", help="stdio | http")) -> None:
    """啟動 MCP server (stdio 預設，給 Claude Code/Cursor; http 給遠端部署)."""
    os.environ["TWMCP_TRANSPORT"] = transport
    from twmcp.server import main

    main()


@app.command(name="id")
def cmd_id(id_number: str) -> None:
    """驗證身分證 / 統一證號."""
    _dump(validate_taiwan_id(id_number))


@app.command(name="tax-id")
def cmd_tax_id(
    tax_id: str,
    rule: str = typer.Option("post-2023", help="post-2023 | pre-2023 | both"),
) -> None:
    """驗證 8 位統一編號 checksum."""
    _dump(validate_tax_id(tax_id, rule=rule))  # type: ignore[arg-type]


@app.command(name="gen-id")
def cmd_gen_id(
    sex: str | None = typer.Option(None, help="male | female | None"),
    city: str = typer.Option("A", help="A-Z 縣市起始字母"),
    seed: int | None = typer.Option(None),
) -> None:
    """產生通過 checksum 的測試身分證 (非真實 PII)."""
    _dump(generate_test_taiwan_id(sex=sex, city_letter=city, seed=seed))  # type: ignore[arg-type]


@app.command(name="gen-tax-id")
def cmd_gen_tax_id(
    rule: str = typer.Option("post-2023"),
    seed: int | None = typer.Option(None),
) -> None:
    """產生通過 checksum 的測試統編 (非真實註冊)."""
    _dump(generate_test_tax_id(rule=rule, seed=seed))  # type: ignore[arg-type]


@app.command(name="addr-normalize")
def cmd_addr_normalize(
    addr: str,
    upgrade_legacy: bool = typer.Option(True, help="自動把高雄縣→高雄市等舊名升格"),
) -> None:
    """正規化台灣地址."""
    _dump(normalize_address(addr, upgrade_legacy=upgrade_legacy))


@app.command(name="legacy-county")
def cmd_legacy_county(name: str) -> None:
    """舊縣名 → 現市名 (如 高雄縣 → 高雄市)."""
    _dump(align_legacy_county(name))


@app.command(name="roc-to-year")
def cmd_roc_to_year(roc: str) -> None:
    """民國年 → 西元年 (支援 '114' / '114-05-04' / '114年5月4日' 等)."""
    _dump(roc_to_western(roc))


@app.command(name="year-to-roc")
def cmd_year_to_roc(year: str) -> None:
    """西元年 → 民國年."""
    _dump(western_to_roc(year))


@app.command(name="s2t")
def cmd_s2t(
    text: str,
    variant: str = typer.Option("zh-tw", help="zh-tw | zh-hk"),
) -> None:
    """簡體中文 → 繁體."""
    typer.echo(simplified_to_traditional(text, variant=variant))  # type: ignore[arg-type]


@app.command(name="t2s")
def cmd_t2s(text: str) -> None:
    """繁體中文 → 簡體."""
    typer.echo(traditional_to_simplified(text))


@app.command(name="num")
def cmd_num(
    text: str,
    direction: str = typer.Option(
        "arabic_to_chinese", help="arabic_to_chinese | chinese_to_arabic"
    ),
    upper: bool = typer.Option(False, help="大寫 (壹貳參)"),
    variant: str = typer.Option("zh-tw", help="zh-tw (繁體, 預設) | zh-cn (簡體)"),
) -> None:
    """阿拉伯數字 ↔ 中文 (公文/合約/支票場景)."""
    typer.echo(
        format_chinese_numerals(text, direction=direction, upper=upper, variant=variant)  # type: ignore[arg-type]
    )


@app.command()
def version() -> None:
    """顯示 twmcp 版本."""
    from twmcp import __version__

    typer.echo(f"twmcp {__version__}")


if __name__ == "__main__":
    app()
