# Report Format

config-schema-guard supports text, Markdown, and JSON reports.

## Text

Text output is meant for terminal reading. It includes summary counts and sections for passed checks, warnings, and errors.

## Markdown

Markdown output is useful for local notes, pull request comments, or saved reports. Review the report before sharing it publicly.

## JSON

JSON output is machine-readable and can be parsed with `json.loads`.

Top-level fields include:

- `tool`
- `version`
- `config_path`
- `schema_path`
- `summary`
- `results`
- `generated_at`

Each result includes:

- `field`
- `rule`
- `severity`
- `passed`
- `message`
- `value_redacted`

## Severity

- `passed`: the rule passed.
- `warning`: non-failing issue, currently used for strict-mode unknown fields.
- `error`: validation failure.

## Exit codes

- `0`: no errors.
- `1`: validation errors were found.
- `2`: CLI, loading, or schema parsing error.

## value_redacted

`value_redacted: true` means the value was intentionally omitted. This happens for sensitive fields and when `--no-values` is used.

## Public sharing note

Reports are local files or terminal output. Before sharing a report publicly, check that it does not contain private paths, sensitive values, or project-specific details you do not want to disclose.

