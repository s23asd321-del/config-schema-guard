from __future__ import annotations

import json

import pytest

from config_schema_guard.schema import SchemaError, load_schema, validate_schema


def test_load_schema(tmp_path):
    path = tmp_path / "schema.json"
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "fields": {
                    "server.port": {
                        "required": True,
                        "type": "integer",
                        "min": 1,
                        "max": 65535,
                    }
                },
            }
        ),
        encoding="utf-8",
    )

    schema = load_schema(path)

    assert schema["version"] == 1
    assert schema["fields"]["server.port"]["type"] == "integer"


def test_schema_requires_fields_object():
    with pytest.raises(SchemaError, match="'fields' must be an object"):
        validate_schema({"version": 1, "fields": []})


def test_schema_rejects_non_object_field_rules():
    with pytest.raises(SchemaError, match="must be an object"):
        validate_schema({"version": 1, "fields": {"app.name": "string"}})


def test_schema_rejects_unsupported_rule_key():
    with pytest.raises(SchemaError, match="unsupported keys"):
        validate_schema({"version": 1, "fields": {"app.name": {"pattern": "x"}}})

