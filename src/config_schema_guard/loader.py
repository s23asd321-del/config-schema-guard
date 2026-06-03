"""Load configuration files without executing their contents."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Any


class ConfigLoadError(ValueError):
    """Raised when a configuration file cannot be loaded."""


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a JSON or TOML configuration file as a dictionary."""

    config_path = Path(path)
    suffix = config_path.suffix.lower()

    if suffix == ".json":
        return _load_json(config_path)
    if suffix == ".toml":
        return _load_toml(config_path)

    raise ConfigLoadError(
        f"Unsupported config format for '{config_path}'. "
        "Supported formats are .json and .toml."
    )


def _load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise ConfigLoadError(f"Config file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ConfigLoadError(f"Invalid JSON config '{path}': {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigLoadError(f"Config file '{path}' must contain a top-level object.")
    return data


def _load_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except FileNotFoundError as exc:
        raise ConfigLoadError(f"Config file not found: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise ConfigLoadError(f"Invalid TOML config '{path}': {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigLoadError(f"Config file '{path}' must contain a top-level object.")
    return data

