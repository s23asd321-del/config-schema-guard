"""Shared data models for validation and reporting."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    """Severity values used in validation results."""

    PASSED = "passed"
    WARNING = "warning"
    ERROR = "error"


@dataclass(frozen=True)
class ValidationResult:
    """A single rule check result."""

    field: str
    rule: str
    severity: Severity
    passed: bool
    message: str
    value_redacted: bool = False
    value: Any | None = None
    description: str | None = None

    def to_dict(self, include_values: bool = True) -> dict[str, Any]:
        item: dict[str, Any] = {
            "field": self.field,
            "rule": self.rule,
            "severity": self.severity.value,
            "passed": self.passed,
            "message": self.message,
            "value_redacted": self.value_redacted,
        }
        if self.description:
            item["description"] = self.description
        if include_values and not self.value_redacted and self.value is not None:
            item["value"] = self.value
        return item


@dataclass(frozen=True)
class ValidationReport:
    """Machine-readable report object."""

    tool: str
    version: str
    config_path: str
    schema_path: str
    summary: dict[str, int]
    results: list[ValidationResult] = field(default_factory=list)
    generated_at: str = ""

    @property
    def has_errors(self) -> bool:
        return self.summary.get("errors", 0) > 0

    def to_dict(self, include_values: bool = True) -> dict[str, Any]:
        return {
            "tool": self.tool,
            "version": self.version,
            "config_path": self.config_path,
            "schema_path": self.schema_path,
            "summary": self.summary,
            "results": [
                result.to_dict(include_values=include_values)
                for result in self.results
            ],
            "generated_at": self.generated_at,
        }
