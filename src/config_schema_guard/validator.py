"""Validate configuration dictionaries against the lightweight schema."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from config_schema_guard.models import Severity, ValidationResult
from config_schema_guard.redaction import should_redact_value

MISSING = object()


def validate_config(
    config: Mapping[str, Any],
    schema: Mapping[str, Any],
    *,
    strict: bool = False,
    no_values: bool = False,
) -> list[ValidationResult]:
    """Validate a loaded config mapping and return rule results."""

    results: list[ValidationResult] = []
    fields = schema.get("fields", {})

    for field_path, rules in fields.items():
        value = get_value_at_path(config, field_path)
        required = bool(rules.get("required", False))
        description = rules.get("description")

        if value is MISSING:
            if required:
                results.append(
                    _result(
                        field_path,
                        "required",
                        Severity.ERROR,
                        False,
                        "Required field is missing.",
                        rules,
                        value=None,
                        description=description,
                        no_values=no_values,
                    )
                )
            continue

        type_ok = True
        if "type" in rules:
            expected_type = rules["type"]
            type_ok = _matches_type(value, expected_type)
            if type_ok:
                results.append(
                    _result(
                        field_path,
                        "type",
                        Severity.PASSED,
                        True,
                        f"Value matches type '{expected_type}'.",
                        rules,
                        value=value,
                        description=description,
                        no_values=no_values,
                    )
                )
            else:
                results.append(
                    _result(
                        field_path,
                        "type",
                        Severity.ERROR,
                        False,
                        f"Expected type '{expected_type}', got '{_type_name(value)}'.",
                        rules,
                        value=value,
                        description=description,
                        no_values=no_values,
                    )
                )

        if "allowed" in rules:
            _check_allowed(results, field_path, rules, value, description, no_values)

        if type_ok:
            _check_min_max(results, field_path, rules, value, description, no_values)
            _check_length(results, field_path, rules, value, description, no_values)
            _check_item_count(results, field_path, rules, value, description, no_values)
            _check_items(results, field_path, rules, value, description, no_values)
            _check_required_children(results, field_path, rules, value, description, no_values)

    if strict:
        results.extend(_find_unknown_fields(config, fields, no_values=no_values))

    return results


def get_value_at_path(config: Mapping[str, Any], field_path: str) -> Any:
    """Read a dot-path value from nested dictionaries."""

    current: Any = config
    for part in field_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return MISSING
        current = current[part]
    return current


def _check_allowed(
    results: list[ValidationResult],
    field_path: str,
    rules: Mapping[str, Any],
    value: Any,
    description: str | None,
    no_values: bool,
) -> None:
    allowed = rules["allowed"]
    if value in allowed:
        results.append(
            _result(
                field_path,
                "allowed",
                Severity.PASSED,
                True,
                "Value is in the allowed list.",
                rules,
                value=value,
                description=description,
                no_values=no_values,
            )
        )
    else:
        results.append(
            _result(
                field_path,
                "allowed",
                Severity.ERROR,
                False,
                "Value is not in the allowed list.",
                rules,
                value=value,
                description=description,
                no_values=no_values,
            )
        )


def _check_min_max(
    results: list[ValidationResult],
    field_path: str,
    rules: Mapping[str, Any],
    value: Any,
    description: str | None,
    no_values: bool,
) -> None:
    if "min" in rules:
        if not _is_number(value):
            results.append(
                _result(
                    field_path,
                    "min",
                    Severity.ERROR,
                    False,
                    "Value is not numeric; cannot apply min.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        elif value < rules["min"]:
            results.append(
                _result(
                    field_path,
                    "min",
                    Severity.ERROR,
                    False,
                    f"Value is less than minimum {rules['min']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        else:
            results.append(
                _result(
                    field_path,
                    "min",
                    Severity.PASSED,
                    True,
                    f"Value is at least {rules['min']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )

    if "max" in rules:
        if not _is_number(value):
            results.append(
                _result(
                    field_path,
                    "max",
                    Severity.ERROR,
                    False,
                    "Value is not numeric; cannot apply max.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        elif value > rules["max"]:
            results.append(
                _result(
                    field_path,
                    "max",
                    Severity.ERROR,
                    False,
                    f"Value is greater than maximum {rules['max']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        else:
            results.append(
                _result(
                    field_path,
                    "max",
                    Severity.PASSED,
                    True,
                    f"Value is at most {rules['max']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )


def _check_length(
    results: list[ValidationResult],
    field_path: str,
    rules: Mapping[str, Any],
    value: Any,
    description: str | None,
    no_values: bool,
) -> None:
    if "min_length" in rules:
        if not isinstance(value, str):
            results.append(
                _result(
                    field_path,
                    "min_length",
                    Severity.ERROR,
                    False,
                    "Value is not a string; cannot apply min_length.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        elif len(value) < rules["min_length"]:
            results.append(
                _result(
                    field_path,
                    "min_length",
                    Severity.ERROR,
                    False,
                    f"String length is less than minimum {rules['min_length']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        else:
            results.append(
                _result(
                    field_path,
                    "min_length",
                    Severity.PASSED,
                    True,
                    f"String length is at least {rules['min_length']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )

    if "max_length" in rules:
        if not isinstance(value, str):
            results.append(
                _result(
                    field_path,
                    "max_length",
                    Severity.ERROR,
                    False,
                    "Value is not a string; cannot apply max_length.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        elif len(value) > rules["max_length"]:
            results.append(
                _result(
                    field_path,
                    "max_length",
                    Severity.ERROR,
                    False,
                    f"String length is greater than maximum {rules['max_length']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        else:
            results.append(
                _result(
                    field_path,
                    "max_length",
                    Severity.PASSED,
                    True,
                    f"String length is at most {rules['max_length']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )


def _check_item_count(
    results: list[ValidationResult],
    field_path: str,
    rules: Mapping[str, Any],
    value: Any,
    description: str | None,
    no_values: bool,
) -> None:
    if "min_items" in rules:
        if not isinstance(value, list):
            results.append(
                _result(
                    field_path,
                    "min_items",
                    Severity.ERROR,
                    False,
                    "Value is not an array; cannot apply min_items.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        elif len(value) < rules["min_items"]:
            results.append(
                _result(
                    field_path,
                    "min_items",
                    Severity.ERROR,
                    False,
                    f"Array length is less than minimum {rules['min_items']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        else:
            results.append(
                _result(
                    field_path,
                    "min_items",
                    Severity.PASSED,
                    True,
                    f"Array length is at least {rules['min_items']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )

    if "max_items" in rules:
        if not isinstance(value, list):
            results.append(
                _result(
                    field_path,
                    "max_items",
                    Severity.ERROR,
                    False,
                    "Value is not an array; cannot apply max_items.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        elif len(value) > rules["max_items"]:
            results.append(
                _result(
                    field_path,
                    "max_items",
                    Severity.ERROR,
                    False,
                    f"Array length is greater than maximum {rules['max_items']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )
        else:
            results.append(
                _result(
                    field_path,
                    "max_items",
                    Severity.PASSED,
                    True,
                    f"Array length is at most {rules['max_items']}.",
                    rules,
                    value=value,
                    description=description,
                    no_values=no_values,
                )
            )


def _check_items(
    results: list[ValidationResult],
    field_path: str,
    rules: Mapping[str, Any],
    value: Any,
    description: str | None,
    no_values: bool,
) -> None:
    if "items" not in rules:
        return

    item_type = rules["items"]["type"]
    if not isinstance(value, list):
        results.append(
            _result(
                field_path,
                "items.type",
                Severity.ERROR,
                False,
                "Value is not an array; cannot apply items.type.",
                rules,
                value=value,
                description=description,
                no_values=no_values,
            )
        )
        return

    mismatches = [
        (index, item)
        for index, item in enumerate(value)
        if not _matches_type(item, item_type)
    ]
    if mismatches:
        index, item = mismatches[0]
        results.append(
            _result(
                field_path,
                "items.type",
                Severity.ERROR,
                False,
                f"Array item at index {index} expected type '{item_type}', got '{_type_name(item)}'.",
                rules,
                value=value,
                description=description,
                no_values=no_values,
            )
        )
    else:
        results.append(
            _result(
                field_path,
                "items.type",
                Severity.PASSED,
                True,
                f"All array items match type '{item_type}'.",
                rules,
                value=value,
                description=description,
                no_values=no_values,
            )
        )


def _check_required_children(
    results: list[ValidationResult],
    field_path: str,
    rules: Mapping[str, Any],
    value: Any,
    description: str | None,
    no_values: bool,
) -> None:
    if "required_children" not in rules:
        return

    if not isinstance(value, Mapping):
        results.append(
            _result(
                field_path,
                "required_children",
                Severity.ERROR,
                False,
                "Value is not an object; cannot apply required_children.",
                rules,
                value=value,
                description=description,
                no_values=no_values,
            )
        )
        return

    missing = [child for child in rules["required_children"] if child not in value]
    if missing:
        joined = ", ".join(missing)
        results.append(
            _result(
                field_path,
                "required_children",
                Severity.ERROR,
                False,
                f"Required child fields are missing: {joined}.",
                rules,
                value=value,
                description=description,
                no_values=no_values,
            )
        )
    else:
        results.append(
            _result(
                field_path,
                "required_children",
                Severity.PASSED,
                True,
                "Required child fields are present.",
                rules,
                value=value,
                description=description,
                no_values=no_values,
            )
        )


def _find_unknown_fields(
    config: Mapping[str, Any],
    fields: Mapping[str, Any],
    *,
    no_values: bool,
) -> list[ValidationResult]:
    known_paths = set(fields)
    results: list[ValidationResult] = []

    for field_path, value in _iter_leaf_paths(config):
        if field_path in known_paths:
            continue
        if _is_allowed_by_declared_object(field_path, fields):
            continue
        if any(known.startswith(f"{field_path}.") for known in known_paths):
            continue

        results.append(
            _result(
                field_path,
                "unknown_field",
                Severity.WARNING,
                False,
                "Field is not declared in the schema.",
                {},
                value=value,
                no_values=no_values,
            )
        )

    return results


def _iter_leaf_paths(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    if isinstance(value, Mapping):
        paths: list[tuple[str, Any]] = []
        for key, child in value.items():
            child_path = f"{prefix}.{key}" if prefix else str(key)
            paths.extend(_iter_leaf_paths(child, child_path))
        return paths
    return [(prefix, value)]


def _is_allowed_by_declared_object(
    field_path: str,
    fields: Mapping[str, Any],
) -> bool:
    parts = field_path.split(".")
    for index in range(1, len(parts)):
        parent = ".".join(parts[:index])
        rules = fields.get(parent)
        if isinstance(rules, Mapping) and rules.get("type") == "object":
            return True
    return False


def _result(
    field_path: str,
    rule: str,
    severity: Severity,
    passed: bool,
    message: str,
    rules: Mapping[str, Any],
    *,
    value: Any | None,
    description: str | None = None,
    no_values: bool = False,
) -> ValidationResult:
    return ValidationResult(
        field=field_path,
        rule=rule,
        severity=severity,
        passed=passed,
        message=message,
        value=value,
        value_redacted=should_redact_value(field_path, rules, no_values=no_values),
        description=description,
    )


def _matches_type(value: Any, expected_type: str) -> bool:
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
        return isinstance(value, Mapping)
    return False


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _type_name(value: Any) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, Mapping):
        return "object"
    if value is None:
        return "null"
    return type(value).__name__
