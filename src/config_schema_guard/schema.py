"""Load and validate the lightweight schema format."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SUPPORTED_TYPES = {
    "string",
    "integer",
    "number",
    "boolean",
    "array",
    "object",
}

SUPPORTED_RULE_KEYS = {
    "required",
    "type",
    "allowed",
    "min",
    "max",
    "min_length",
    "max_length",
    "sensitive",
    "description",
}


class SchemaError(ValueError):
    """Raised when a schema file is invalid."""


def load_schema(path: str | Path) -> dict[str, Any]:
    """Load and validate a schema JSON file."""

    schema_path = Path(path)
    if schema_path.suffix.lower() != ".json":
        raise SchemaError(
            f"Unsupported schema format for '{schema_path}'. "
            "Schema files must be JSON in version 1."
        )

    try:
        with schema_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise SchemaError(f"Schema file not found: {schema_path}") from exc
    except json.JSONDecodeError as exc:
        raise SchemaError(f"Invalid JSON schema '{schema_path}': {exc}") from exc

    validate_schema(data)
    return data


def validate_schema(schema: Any) -> None:
    """Validate basic schema structure and supported rule keys."""

    if not isinstance(schema, dict):
        raise SchemaError("Schema must be a JSON object.")

    version = schema.get("version")
    if version != 1:
        raise SchemaError("Schema version must be 1.")

    fields = schema.get("fields")
    if not isinstance(fields, dict):
        raise SchemaError("Schema 'fields' must be an object.")

    for field_path, rules in fields.items():
        if not isinstance(field_path, str) or not field_path:
            raise SchemaError("Every field path must be a non-empty string.")
        if not isinstance(rules, dict):
            raise SchemaError(f"Rules for '{field_path}' must be an object.")
        _validate_field_rules(field_path, rules)


def _validate_field_rules(field_path: str, rules: dict[str, Any]) -> None:
    unknown_keys = sorted(set(rules) - SUPPORTED_RULE_KEYS)
    if unknown_keys:
        joined = ", ".join(unknown_keys)
        raise SchemaError(f"Rules for '{field_path}' contain unsupported keys: {joined}.")

    if "required" in rules and not isinstance(rules["required"], bool):
        raise SchemaError(f"Rule 'required' for '{field_path}' must be boolean.")

    if "type" in rules:
        field_type = rules["type"]
        if field_type not in SUPPORTED_TYPES:
            supported = ", ".join(sorted(SUPPORTED_TYPES))
            raise SchemaError(
                f"Rule 'type' for '{field_path}' must be one of: {supported}."
            )

    if "allowed" in rules and not isinstance(rules["allowed"], list):
        raise SchemaError(f"Rule 'allowed' for '{field_path}' must be a list.")

    for rule_name in ("min", "max"):
        if rule_name in rules and not _is_number(rules[rule_name]):
            raise SchemaError(f"Rule '{rule_name}' for '{field_path}' must be numeric.")

    for rule_name in ("min_length", "max_length"):
        if rule_name in rules:
            value = rules[rule_name]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise SchemaError(
                    f"Rule '{rule_name}' for '{field_path}' must be a non-negative integer."
                )

    if "sensitive" in rules and not isinstance(rules["sensitive"], bool):
        raise SchemaError(f"Rule 'sensitive' for '{field_path}' must be boolean.")

    if "description" in rules and not isinstance(rules["description"], str):
        raise SchemaError(f"Rule 'description' for '{field_path}' must be a string.")


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)

