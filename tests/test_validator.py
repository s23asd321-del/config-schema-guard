from __future__ import annotations

from pathlib import Path

from config_schema_guard.loader import load_config
from config_schema_guard.schema import load_schema
from config_schema_guard.validator import validate_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def schema_with(fields):
    return {"version": 1, "fields": fields}


def result_for(results, field, rule):
    matches = [item for item in results if item.field == field and item.rule == rule]
    assert matches, f"Missing result for {field}:{rule}"
    return matches[0]


def test_required_field_missing_produces_error():
    schema = schema_with({"app.name": {"required": True, "type": "string"}})

    results = validate_config({"app": {}}, schema)

    result = result_for(results, "app.name", "required")
    assert not result.passed
    assert result.severity.value == "error"


def test_type_mismatch_produces_error():
    schema = schema_with({"app.debug": {"required": True, "type": "boolean"}})

    results = validate_config({"app": {"debug": "yes"}}, schema)

    result = result_for(results, "app.debug", "type")
    assert not result.passed
    assert "Expected type 'boolean'" in result.message


def test_allowed_value_mismatch_produces_error():
    schema = schema_with(
        {"logging.level": {"required": False, "type": "string", "allowed": ["info"]}}
    )

    results = validate_config({"logging": {"level": "trace"}}, schema)

    result = result_for(results, "logging.level", "allowed")
    assert not result.passed


def test_min_and_max_mismatch_produce_errors():
    schema = schema_with({"server.port": {"required": True, "type": "integer", "min": 1, "max": 10}})

    low_results = validate_config({"server": {"port": 0}}, schema)
    high_results = validate_config({"server": {"port": 11}}, schema)

    assert not result_for(low_results, "server.port", "min").passed
    assert not result_for(high_results, "server.port", "max").passed


def test_min_length_and_max_length_mismatch_produce_errors():
    schema = schema_with(
        {
            "app.name": {
                "required": True,
                "type": "string",
                "min_length": 3,
                "max_length": 5,
            }
        }
    )

    short_results = validate_config({"app": {"name": "ab"}}, schema)
    long_results = validate_config({"app": {"name": "abcdef"}}, schema)

    assert not result_for(short_results, "app.name", "min_length").passed
    assert not result_for(long_results, "app.name", "max_length").passed


def test_optional_missing_field_does_not_produce_error():
    schema = schema_with({"logging.level": {"required": False, "type": "string"}})

    results = validate_config({}, schema)

    assert results == []


def test_strict_mode_finds_unknown_field_warning():
    schema = schema_with({"app.name": {"required": True, "type": "string"}})

    results = validate_config(
        {"app": {"name": "demo", "extra": True}},
        schema,
        strict=True,
    )

    result = result_for(results, "app.extra", "unknown_field")
    assert result.severity.value == "warning"


def test_non_strict_mode_ignores_unknown_field():
    schema = schema_with({"app.name": {"required": True, "type": "string"}})

    results = validate_config(
        {"app": {"name": "demo", "extra": True}},
        schema,
        strict=False,
    )

    assert all(item.rule != "unknown_field" for item in results)
    assert all(item.severity.value != "error" for item in results)


def test_examples_good_and_bad_configs_behave_as_expected():
    schema = load_schema(PROJECT_ROOT / "examples/schema/basic.schema.json")
    good_json = load_config(PROJECT_ROOT / "examples/good-config/config.json")
    good_toml = load_config(PROJECT_ROOT / "examples/good-config/config.toml")
    bad_json = load_config(PROJECT_ROOT / "examples/bad-config/config.json")
    bad_toml = load_config(PROJECT_ROOT / "examples/bad-config/config.toml")

    assert not any(item.severity.value == "error" for item in validate_config(good_json, schema))
    assert not any(item.severity.value == "error" for item in validate_config(good_toml, schema))
    assert any(item.severity.value == "error" for item in validate_config(bad_json, schema))
    assert any(item.severity.value == "error" for item in validate_config(bad_toml, schema))

