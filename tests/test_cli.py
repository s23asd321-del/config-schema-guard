from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from config_schema_guard.cli import main

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "examples/schema/basic.schema.json"


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "-m", "config_schema_guard.cli", *args],
        cwd=PROJECT_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_cli_good_config_returns_zero():
    completed = run_cli("check", "examples/good-config/config.json", "--schema", SCHEMA)

    assert completed.returncode == 0
    assert "Errors:   0" in completed.stdout


def test_cli_main_good_config_returns_zero(capsys):
    code = main(
        [
            "check",
            str(PROJECT_ROOT / "examples/good-config/config.json"),
            "--schema",
            str(PROJECT_ROOT / SCHEMA),
        ]
    )

    captured = capsys.readouterr()
    assert code == 0
    assert "Errors:   0" in captured.out


def test_cli_bad_config_returns_one():
    completed = run_cli("check", "examples/bad-config/config.json", "--schema", SCHEMA)

    assert completed.returncode == 1
    assert "Errors:" in completed.stdout


def test_cli_version_outputs_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])

    captured = capsys.readouterr()
    assert exc_info.value.code == 0
    assert "config-guard 0.1.0" in captured.out


def test_cli_output_writes_report_file(tmp_path):
    output_path = tmp_path / "report.json"

    completed = run_cli(
        "check",
        "examples/good-config/config.json",
        "--schema",
        SCHEMA,
        "--format",
        "json",
        "--output",
        str(output_path),
    )

    assert completed.returncode == 0
    assert completed.stdout == ""
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["summary"]["errors"] == 0


def test_cli_main_accepts_toml_schema(capsys):
    code = main(
        [
            "check",
            str(PROJECT_ROOT / "examples/good-config/config.toml"),
            "--schema",
            str(PROJECT_ROOT / "examples/schema/basic.schema.toml"),
        ]
    )

    captured = capsys.readouterr()
    assert code == 0
    assert "Errors:   0" in captured.out


def test_cli_output_refuses_to_overwrite_without_force(tmp_path):
    output_path = tmp_path / "report.json"
    output_path.write_text("existing\n", encoding="utf-8")

    completed = run_cli(
        "check",
        "examples/good-config/config.json",
        "--schema",
        SCHEMA,
        "--format",
        "json",
        "--output",
        str(output_path),
    )

    assert completed.returncode == 2
    assert "already exists" in completed.stderr
    assert output_path.read_text(encoding="utf-8") == "existing\n"


def test_cli_main_output_refuses_to_overwrite_without_force(tmp_path, capsys):
    output_path = tmp_path / "report.json"
    output_path.write_text("existing\n", encoding="utf-8")

    code = main(
        [
            "check",
            str(PROJECT_ROOT / "examples/good-config/config.json"),
            "--schema",
            str(PROJECT_ROOT / SCHEMA),
            "--format",
            "json",
            "--output",
            str(output_path),
        ]
    )

    captured = capsys.readouterr()
    assert code == 2
    assert "already exists" in captured.err
    assert output_path.read_text(encoding="utf-8") == "existing\n"


def test_cli_output_force_overwrites_existing_file(tmp_path):
    output_path = tmp_path / "report.json"
    output_path.write_text("existing\n", encoding="utf-8")

    completed = run_cli(
        "check",
        "examples/good-config/config.json",
        "--schema",
        SCHEMA,
        "--format",
        "json",
        "--output",
        str(output_path),
        "--force",
    )

    assert completed.returncode == 0
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["summary"]["errors"] == 0


def test_cli_bad_toml_json_report_returns_one_and_is_parseable():
    completed = run_cli(
        "check",
        "examples/bad-config/config.toml",
        "--schema",
        SCHEMA,
        "--format",
        "json",
    )

    assert completed.returncode == 1
    data = json.loads(completed.stdout)
    assert data["summary"]["errors"] > 0
