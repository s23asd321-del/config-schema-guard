"""Sensitive field detection and value redaction helpers."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

SENSITIVE_NAME_PARTS = (
    "password",
    "secret",
    "token",
    "key",
    "cookie",
    "credential",
)


def is_sensitive_field(
    field_path: str,
    rule: Mapping[str, Any] | None = None,
) -> bool:
    """Return True when a field should be treated as sensitive."""

    if rule and rule.get("sensitive") is True:
        return True

    normalized = field_path.lower()
    return any(part in normalized for part in SENSITIVE_NAME_PARTS)


def should_redact_value(
    field_path: str,
    rule: Mapping[str, Any] | None = None,
    no_values: bool = False,
) -> bool:
    """Return True when a report must omit the field value."""

    return no_values or is_sensitive_field(field_path, rule)

