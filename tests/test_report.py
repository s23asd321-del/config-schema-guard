from __future__ import annotations

import json

from config_schema_guard.report import build_report, render_json, render_markdown, render_text
from config_schema_guard.validator import validate_config


def test_markdown_report_does_not_contain_sensitive_value():
    schema = {
        "version": 1,
        "fields": {
            "auth.token": {
                "required": True,
                "type": "string",
                "sensitive": True,
            }
        },
    }
    results = validate_config({"auth": {"token": "SHOULD_NOT_APPEAR"}}, schema)
    report = build_report(config_path="config.json", schema_path="schema.json", results=results)

    output = render_markdown(report)

    assert "SHOULD_NOT_APPEAR" not in output
    assert "auth.token" in output


def test_text_report_does_not_contain_sensitive_value():
    schema = {
        "version": 1,
        "fields": {
            "auth.token": {
                "required": True,
                "type": "string",
                "sensitive": True,
            }
        },
    }
    results = validate_config({"auth": {"token": "SHOULD_NOT_APPEAR"}}, schema)
    report = build_report(config_path="config.json", schema_path="schema.json", results=results)

    output = render_text(report)

    assert "SHOULD_NOT_APPEAR" not in output


def test_json_report_can_be_loaded_with_json_loads():
    schema = {"version": 1, "fields": {"app.name": {"required": True, "type": "string"}}}
    results = validate_config({"app": {"name": "demo"}}, schema)
    report = build_report(config_path="config.json", schema_path="schema.json", results=results)

    output = render_json(report)
    data = json.loads(output)

    assert data["tool"] == "config-schema-guard"
    assert data["results"][0]["field"] == "app.name"

