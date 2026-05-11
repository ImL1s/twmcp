"""跨平台 cache / config 路徑 (per Gemini 3.1 Pro best practice #6).

macOS:   ~/Library/Caches/twmcp/
Linux:   ~/.cache/twmcp/
Windows: %LOCALAPPDATA%\\twmcp\\twmcp\\Cache
"""

from __future__ import annotations

import os
from pathlib import Path

from platformdirs import user_cache_dir, user_config_dir, user_data_dir

APP_NAME = "twmcp"
APP_AUTHOR = "twmcp"


def cache_dir() -> Path:
    """Per-user cache directory. Use TWMCP_CACHE_DIR env to override."""
    override = os.environ.get("TWMCP_CACHE_DIR")
    if override:
        return Path(override).expanduser()
    return Path(user_cache_dir(APP_NAME, APP_AUTHOR))


def config_dir() -> Path:
    """Per-user config directory. Use TWMCP_CONFIG_DIR env to override."""
    override = os.environ.get("TWMCP_CONFIG_DIR")
    if override:
        return Path(override).expanduser()
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))


def data_dir() -> Path:
    """Per-user data directory (for downloaded open data indices)."""
    override = os.environ.get("TWMCP_DATA_DIR")
    if override:
        return Path(override).expanduser()
    return Path(user_data_dir(APP_NAME, APP_AUTHOR))


def ensure(path: Path) -> Path:
    """Mkdir -p; return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path
