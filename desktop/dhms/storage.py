"""Small per-user settings store. Original data is never copied or deleted."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

from .core import DataError


def workspace_path() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home()/"AppData"/"Local"))
    elif sys.platform == "darwin":
        base = Path.home()/"Library"/"Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home()/".local"/"share"))
    return base/"DHMS-Desktop"


def load_settings() -> dict:
    path = workspace_path()/"settings.json"
    try:
        if path.stat().st_size > 16_384:
            return {}
        value = json.loads(path.read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def save_settings(settings: dict) -> None:
    """Replace settings only after valid bounded JSON is flushed to disk."""
    if not isinstance(settings, dict):
        raise DataError("Settings must be a JSON object.")
    try:
        content = json.dumps(settings, ensure_ascii=False, allow_nan=False, indent=2)
    except (TypeError, ValueError) as exc:
        raise DataError("Settings must contain finite JSON values.") from exc
    if len(content.encode("utf-8")) > 16_384:
        raise DataError("Settings exceed the 16 KiB limit.")
    folder = workspace_path()
    temp = None
    try:
        folder.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=folder, prefix=".settings-", suffix=".tmp", delete=False) as stream:
            temp = Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, folder/"settings.json")
    except OSError as exc:
        raise DataError(f"Cannot save settings: {exc.strerror or type(exc).__name__}.") from exc
    finally:
        if temp and temp.exists():
            temp.unlink()
