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


def test_load_toml_schema(tmp_path):
    path = tmp_path / "schema.toml"
    path.write_text(
        """
version = 1

[fields."server.port"]
required = true
type = "integer"
min = 1
max = 65535
""".strip(),
        encoding="utf-8",
    )

    schema = load_schema(path)

    assert schema["version"] == 1
    assert schema["fields"]["server.port"]["max"] == 65535


def test_schema_requires_fields_object():
    with pytest.raises(SchemaError, match="'fields' must be an object"):
        validate_schema({"version": 1, "fields": []})


def test_schema_rejects_non_object_field_rules():
    with pytest.raises(SchemaError, match="must be an object"):
        validate_schema({"version": 1, "fields": {"app.name": "string"}})


def test_schema_rejects_unsupported_rule_key():
    with pytest.raises(SchemaError, match="unsupported keys"):
        validate_schema({"version": 1, "fields": {"app.name": {"pattern": "x"}}})


def test_schema_rejects_min_greater_than_max():
    with pytest.raises(SchemaError, match="less than or equal to 'max'"):
        validate_schema(
            {
                "version": 1,
                "fields": {"server.port": {"type": "integer", "min": 10, "max": 1}},
            }
        )


def test_schema_rejects_min_on_non_numeric_type():
    with pytest.raises(SchemaError, match="require type 'integer' or 'number'"):
        validate_schema(
            {
                "version": 1,
                "fields": {"app.name": {"type": "string", "min": 1}},
            }
        )


def test_schema_rejects_min_length_on_non_string_type():
    with pytest.raises(SchemaError, match="require type 'string'"):
        validate_schema(
            {
                "version": 1,
                "fields": {"server.port": {"type": "integer", "min_length": 1}},
            }
        )


def test_schema_rejects_min_length_greater_than_max_length():
    with pytest.raises(SchemaError, match="less than or equal to 'max_length'"):
        validate_schema(
            {
                "version": 1,
                "fields": {"app.name": {"type": "string", "min_length": 5, "max_length": 3}},
            }
        )


def test_schema_rejects_allowed_value_type_mismatch():
    with pytest.raises(SchemaError, match="does not match type 'integer'"):
        validate_schema(
            {
                "version": 1,
                "fields": {"server.port": {"type": "integer", "allowed": [8080, "bad"]}},
            }
        )


def test_schema_rejects_array_rules_on_non_array_type():
    with pytest.raises(SchemaError, match="require type 'array'"):
        validate_schema(
            {
                "version": 1,
                "fields": {"labels": {"type": "string", "items": {"type": "string"}}},
            }
        )


def test_schema_rejects_min_items_greater_than_max_items():
    with pytest.raises(SchemaError, match="less than or equal to 'max_items'"):
        validate_schema(
            {
                "version": 1,
                "fields": {"labels": {"type": "array", "min_items": 3, "max_items": 1}},
            }
        )


def test_schema_rejects_required_children_on_non_object_type():
    with pytest.raises(SchemaError, match="requires type 'object'"):
        validate_schema(
            {
                "version": 1,
                "fields": {"metadata": {"type": "array", "required_children": ["owner"]}},
            }
        )
