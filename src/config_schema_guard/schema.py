"""Load and validate the lightweight schema format."""

from __future__ import annotations

import json
import tomllib
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
    "items",
    "min_items",
    "max_items",
    "required_children",
}


class SchemaError(ValueError):
    """Raised when a schema file is invalid."""


def load_schema(path: str | Path) -> dict[str, Any]:
    """Load and validate a schema JSON or TOML file."""

    schema_path = Path(path)
    suffix = schema_path.suffix.lower()

    if suffix == ".json":
        data = _load_schema_json(schema_path)
    elif suffix == ".toml":
        data = _load_schema_toml(schema_path)
    else:
        raise SchemaError(
            f"Unsupported schema format for '{schema_path}'. "
            "Schema files must be .json or .toml in version 1."
        )

    validate_schema(data)
    return data


def _load_schema_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except FileNotFoundError as exc:
        raise SchemaError(f"Schema file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SchemaError(f"Invalid JSON schema '{path}': {exc}") from exc

    if not isinstance(data, dict):
        raise SchemaError(f"Schema file '{path}' must contain a top-level object.")
    return data


def _load_schema_toml(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            data = tomllib.load(handle)
    except FileNotFoundError as exc:
        raise SchemaError(f"Schema file not found: {path}") from exc
    except tomllib.TOMLDecodeError as exc:
        raise SchemaError(f"Invalid TOML schema '{path}': {exc}") from exc

    if not isinstance(data, dict):
        raise SchemaError(f"Schema file '{path}' must contain a top-level object.")
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

    field_type = rules.get("type")
    if field_type is not None:
        if field_type not in SUPPORTED_TYPES:
            supported = ", ".join(sorted(SUPPORTED_TYPES))
            raise SchemaError(
                f"Rule 'type' for '{field_path}' must be one of: {supported}."
            )

    _validate_allowed(field_path, rules, field_type)
    _validate_numeric_rules(field_path, rules, field_type)
    _validate_string_length_rules(field_path, rules, field_type)
    _validate_array_rules(field_path, rules, field_type)
    _validate_object_rules(field_path, rules, field_type)

    if "sensitive" in rules and not isinstance(rules["sensitive"], bool):
        raise SchemaError(f"Rule 'sensitive' for '{field_path}' must be boolean.")

    if "description" in rules and not isinstance(rules["description"], str):
        raise SchemaError(f"Rule 'description' for '{field_path}' must be a string.")


def _validate_allowed(
    field_path: str,
    rules: dict[str, Any],
    field_type: Any,
) -> None:
    if "allowed" not in rules:
        return

    allowed = rules["allowed"]
    if not isinstance(allowed, list):
        raise SchemaError(f"Rule 'allowed' for '{field_path}' must be a list.")

    if field_type in SUPPORTED_TYPES:
        for index, item in enumerate(allowed):
            if not _matches_schema_type(item, field_type):
                raise SchemaError(
                    f"Rule 'allowed' item {index} for '{field_path}' "
                    f"does not match type '{field_type}'."
                )


def _validate_numeric_rules(
    field_path: str,
    rules: dict[str, Any],
    field_type: Any,
) -> None:
    if "min" in rules or "max" in rules:
        if field_type not in {"integer", "number"}:
            raise SchemaError(
                f"Rules 'min' and 'max' for '{field_path}' require type "
                "'integer' or 'number'."
            )

    for rule_name in ("min", "max"):
        if rule_name in rules and not _is_number(rules[rule_name]):
            raise SchemaError(f"Rule '{rule_name}' for '{field_path}' must be numeric.")

    if "min" in rules and "max" in rules and rules["min"] > rules["max"]:
        raise SchemaError(f"Rule 'min' for '{field_path}' must be less than or equal to 'max'.")


def _validate_string_length_rules(
    field_path: str,
    rules: dict[str, Any],
    field_type: Any,
) -> None:
    if "min_length" in rules or "max_length" in rules:
        if field_type != "string":
            raise SchemaError(
                f"Rules 'min_length' and 'max_length' for '{field_path}' require type 'string'."
            )

    for rule_name in ("min_length", "max_length"):
        if rule_name in rules:
            value = rules[rule_name]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise SchemaError(
                    f"Rule '{rule_name}' for '{field_path}' must be a non-negative integer."
                )

    if (
        "min_length" in rules
        and "max_length" in rules
        and rules["min_length"] > rules["max_length"]
    ):
        raise SchemaError(
            f"Rule 'min_length' for '{field_path}' must be less than or equal to 'max_length'."
        )


def _validate_array_rules(
    field_path: str,
    rules: dict[str, Any],
    field_type: Any,
) -> None:
    if any(rule_name in rules for rule_name in ("items", "min_items", "max_items")):
        if field_type != "array":
            raise SchemaError(
                f"Rules 'items', 'min_items', and 'max_items' for '{field_path}' "
                "require type 'array'."
            )

    if "items" in rules:
        items = rules["items"]
        if not isinstance(items, dict):
            raise SchemaError(f"Rule 'items' for '{field_path}' must be an object.")
        unknown_keys = sorted(set(items) - {"type"})
        if unknown_keys:
            joined = ", ".join(unknown_keys)
            raise SchemaError(
                f"Rule 'items' for '{field_path}' contains unsupported keys: {joined}."
            )
        item_type = items.get("type")
        if item_type not in SUPPORTED_TYPES:
            supported = ", ".join(sorted(SUPPORTED_TYPES))
            raise SchemaError(
                f"Rule 'items.type' for '{field_path}' must be one of: {supported}."
            )

    for rule_name in ("min_items", "max_items"):
        if rule_name in rules:
            value = rules[rule_name]
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise SchemaError(
                    f"Rule '{rule_name}' for '{field_path}' must be a non-negative integer."
                )

    if "min_items" in rules and "max_items" in rules and rules["min_items"] > rules["max_items"]:
        raise SchemaError(
            f"Rule 'min_items' for '{field_path}' must be less than or equal to 'max_items'."
        )


def _validate_object_rules(
    field_path: str,
    rules: dict[str, Any],
    field_type: Any,
) -> None:
    if "required_children" not in rules:
        return

    if field_type != "object":
        raise SchemaError(f"Rule 'required_children' for '{field_path}' requires type 'object'.")

    children = rules["required_children"]
    if not isinstance(children, list):
        raise SchemaError(f"Rule 'required_children' for '{field_path}' must be a list.")

    for child in children:
        if not isinstance(child, str) or not child or "." in child:
            raise SchemaError(
                f"Rule 'required_children' for '{field_path}' must contain "
                "non-empty immediate child names."
            )


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _matches_schema_type(value: Any, expected_type: str) -> bool:
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected_type == "number":
        return _is_number(value)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "array":
        return isinstance(value, list)
    if expected_type == "object":
        return isinstance(value, dict)
    return False
