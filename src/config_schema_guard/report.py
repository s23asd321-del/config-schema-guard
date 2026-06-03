"""Render validation reports in text, Markdown, and JSON formats."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from config_schema_guard import __version__
from config_schema_guard.models import Severity, ValidationReport, ValidationResult


def build_report(
    *,
    config_path: str | Path,
    schema_path: str | Path,
    results: list[ValidationResult],
) -> ValidationReport:
    """Build a report with summary counts and a timestamp."""

    summary = {
        "total": len(results),
        "passed": sum(1 for result in results if result.passed),
        "warnings": sum(1 for result in results if result.severity == Severity.WARNING),
        "errors": sum(1 for result in results if result.severity == Severity.ERROR),
    }
    return ValidationReport(
        tool="config-schema-guard",
        version=__version__,
        config_path=str(config_path),
        schema_path=str(schema_path),
        summary=summary,
        results=results,
        generated_at=datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    )


def render_report(
    report: ValidationReport,
    *,
    output_format: str,
    include_values: bool = True,
) -> str:
    """Render a report in the requested format."""

    if output_format == "text":
        return render_text(report, include_values=include_values)
    if output_format == "markdown":
        return render_markdown(report, include_values=include_values)
    if output_format == "json":
        return render_json(report, include_values=include_values)
    raise ValueError(f"Unsupported report format: {output_format}")


def render_text(report: ValidationReport, *, include_values: bool = True) -> str:
    """Render a terminal-friendly text report."""

    lines = [
        "Config Schema Guard Report",
        "",
        "Summary:",
        f"  Passed:   {report.summary['passed']}",
        f"  Warnings: {report.summary['warnings']}",
        f"  Errors:   {report.summary['errors']}",
        "",
    ]

    lines.extend(_text_section("Passed checks", _filter(report, Severity.PASSED), include_values))
    lines.extend(_text_section("Warnings", _filter(report, Severity.WARNING), include_values))
    lines.extend(_text_section("Errors", _filter(report, Severity.ERROR), include_values))
    lines.append("Sensitive values are redacted when fields are marked sensitive or look sensitive by name.")
    return "\n".join(lines)


def render_markdown(report: ValidationReport, *, include_values: bool = True) -> str:
    """Render a Markdown report."""

    lines = [
        "# Config Schema Guard Report",
        "",
        "## Summary",
        "",
        f"- Passed checks: {report.summary['passed']}",
        f"- Warnings: {report.summary['warnings']}",
        f"- Errors: {report.summary['errors']}",
        "",
    ]

    lines.extend(_markdown_section("Passed checks", _filter(report, Severity.PASSED), include_values))
    lines.extend(_markdown_section("Warnings", _filter(report, Severity.WARNING), include_values))
    lines.extend(_markdown_section("Errors", _filter(report, Severity.ERROR), include_values))
    lines.extend(
        [
            "## Recommendations",
            "",
            "- Fix errors before relying on the checked configuration.",
            "- Review warnings when strict mode is enabled.",
            "- Keep schema files small, versioned, and close to example configs.",
            "",
            "## Sensitive value handling note",
            "",
            "Values are omitted when fields are marked `sensitive: true`, when field names look sensitive, or when `--no-values` is used.",
        ]
    )
    return "\n".join(lines)


def render_json(report: ValidationReport, *, include_values: bool = True) -> str:
    """Render a JSON report that can be parsed by json.loads."""

    return json.dumps(report.to_dict(include_values=include_values), indent=2, sort_keys=True)


def _filter(report: ValidationReport, severity: Severity) -> list[ValidationResult]:
    return [result for result in report.results if result.severity == severity]


def _text_section(
    title: str,
    results: list[ValidationResult],
    include_values: bool,
) -> list[str]:
    lines = [f"{title}:"]
    if not results:
        lines.extend(["  None", ""])
        return lines

    for result in results:
        lines.append(f"  - field: {result.field}")
        lines.append(f"    rule: {result.rule}")
        lines.append(f"    severity: {result.severity.value}")
        lines.append(f"    message: {result.message}")
        value_text = _safe_value_text(result, include_values)
        if value_text is not None:
            lines.append(f"    value: {value_text}")
    lines.append("")
    return lines


def _markdown_section(
    title: str,
    results: list[ValidationResult],
    include_values: bool,
) -> list[str]:
    lines = [f"## {title}", ""]
    if not results:
        lines.extend(["None.", ""])
        return lines

    for result in results:
        line = (
            f"- `{result.field}`: `{result.rule}` "
            f"({result.severity.value}) - {result.message}"
        )
        value_text = _safe_value_text(result, include_values)
        if value_text is not None:
            line = f"{line} Value: `{value_text}`."
        lines.append(line)
    lines.append("")
    return lines


def _safe_value_text(result: ValidationResult, include_values: bool) -> str | None:
    if not include_values or result.value_redacted or result.value is None:
        return None
    return repr(result.value)

