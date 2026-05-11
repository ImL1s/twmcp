"""跨平台路徑 utility 測試."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from twmcp.utils.paths import cache_dir, config_dir, data_dir, ensure


def test_cache_dir_is_user_specific():
    p = cache_dir()
    assert isinstance(p, Path)
    home = Path.home()
    # Either under HOME or (on systems where platformdirs returns elsewhere) at least
    # absolute path with twmcp in it
    assert "twmcp" in str(p)
    # 多數 OS 下會在 home 之下
    if sys.platform != "win32":
        assert str(p).startswith(str(home)) or str(p).startswith("/tmp")


def test_env_override(tmp_path, monkeypatch):
    monkeypatch.setenv("TWMCP_CACHE_DIR", str(tmp_path / "custom_cache"))
    assert cache_dir() == tmp_path / "custom_cache"


def test_env_override_expands_user(monkeypatch):
    monkeypatch.setenv("TWMCP_CONFIG_DIR", "~/some_dir")
    p = config_dir()
    assert "~" not in str(p)


def test_ensure_creates_dir(tmp_path):
    target = tmp_path / "a" / "b" / "c"
    assert not target.exists()
    out = ensure(target)
    assert out == target
    assert target.is_dir()


def test_data_dir_default(monkeypatch):
    monkeypatch.delenv("TWMCP_DATA_DIR", raising=False)
    p = data_dir()
    assert "twmcp" in str(p)
