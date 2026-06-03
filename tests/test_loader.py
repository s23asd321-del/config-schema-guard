from __future__ import annotations

import pytest

from config_schema_guard.loader import ConfigLoadError, load_config


def test_load_json_config(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"app": {"debug": false}}', encoding="utf-8")

    config = load_config(path)

    assert config == {"app": {"debug": False}}


def test_load_toml_config(tmp_path):
    path = tmp_path / "config.toml"
    path.write_text("[app]\ndebug = false\n", encoding="utf-8")

    config = load_config(path)

    assert config == {"app": {"debug": False}}


def test_unsupported_config_format_raises_clear_error(tmp_path):
    path = tmp_path / "config.yaml"
    path.write_text("app:\n  debug: false\n", encoding="utf-8")

    with pytest.raises(ConfigLoadError, match="Supported formats are .json and .toml"):
        load_config(path)

