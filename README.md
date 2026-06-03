# config-schema-guard

config-schema-guard is a local-first CLI for lightweight JSON and TOML configuration structure validation.

It checks whether a config file follows a small, readable, versioned schema file. It is intended for projects that want a simple guardrail before running local tools, examples, tests, or CI jobs.

## Project positioning

config-schema-guard is a developer utility for checking expected config shape, required fields, basic types, allowed values, numeric ranges, and string lengths.

It is useful for:

- Local checks before running a tool or application.
- CI checks for `config.example.json` or `config.example.toml`.
- Open source projects that want example configs to stay complete.
- Teaching projects that need an approachable validation example.
- Small tools that want to fail earlier when config fields are missing or malformed.

## What it can do

- Load local JSON and TOML config files.
- Load a local schema JSON file.
- Validate dot-path fields such as `server.port`.
- Check `required`, `type`, `allowed`, `min`, `max`, `min_length`, and `max_length`.
- Redact sensitive values in reports.
- Produce text, Markdown, and JSON reports.
- Return CI-friendly exit codes.

## What it cannot do

- It is not a security scanner.
- It is not a secret scanner.
- It is not a privacy compliance tool.
- It is not a vulnerability scanner.
- It is not a full JSON Schema replacement.
- It is not a cloud configuration platform.
- It does not execute config content.
- It does not connect to the network.
- It does not upload files.
- It does not collect telemetry.

## Why not full JSON Schema?

Full JSON Schema is powerful and broadly useful, but it can be more than a small project needs for example config checks. This project intentionally starts with a smaller custom format that is easy to read, easy to version, and simple to explain.

For advanced validation, broad ecosystem compatibility, or formal schema requirements, use JSON Schema and a mature validator.

## Installation

From a future package release:

```bash
python -m pip install config-schema-guard
```

For the current repository checkout:

```bash
python -m pip install -e .
```

## Local development install

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Quick start

```bash
python -m config_schema_guard.cli check examples/good-config/config.json --schema examples/schema/basic.schema.json
```

With the console entry point:

```bash
config-guard check examples/good-config/config.json --schema examples/schema/basic.schema.json
```

## JSON config example

```json
{
  "app": {
    "name": "demo-service",
    "debug": false,
    "description": "Example app configuration"
  },
  "server": {
    "host": "localhost",
    "port": 8080
  },
  "logging": {
    "level": "info"
  },
  "auth": {
    "token": "FAKE_TOKEN_FOR_TESTING_ONLY"
  }
}
```

## TOML config example

```toml
[app]
name = "demo-service"
debug = false
description = "Example app configuration"

[server]
host = "localhost"
port = 8080

[logging]
level = "info"

[auth]
token = "FAKE_TOKEN_FOR_TESTING_ONLY"
```

## Schema example

```json
{
  "version": 1,
  "name": "basic app config",
  "fields": {
    "app.name": {
      "required": true,
      "type": "string",
      "min_length": 3,
      "max_length": 40,
      "description": "Application name"
    },
    "server.port": {
      "required": true,
      "type": "integer",
      "min": 1,
      "max": 65535
    },
    "logging.level": {
      "required": false,
      "type": "string",
      "allowed": ["debug", "info", "warning", "error"]
    },
    "auth.token": {
      "required": false,
      "type": "string",
      "sensitive": true
    }
  }
}
```

## CLI usage

```bash
config-guard check <config-path> --schema <schema-path>
```

Options:

- `--format text`: terminal-oriented output.
- `--format markdown`: Markdown report output.
- `--format json`: machine-readable JSON report.
- `--output <file>`: write the report to a local file.
- `--strict`: report schema-unknown fields as warnings.
- `--no-values`: omit all config values from the report.

Examples:

```bash
python -m config_schema_guard.cli check examples/good-config/config.json --schema examples/schema/basic.schema.json
python -m config_schema_guard.cli check examples/bad-config/config.json --schema examples/schema/basic.schema.json --format markdown
python -m config_schema_guard.cli check examples/bad-config/config.toml --schema examples/schema/basic.schema.json --format json
```

## Report examples

Text:

```text
Config Schema Guard Report

Summary:
  Passed:   12
  Warnings: 0
  Errors:   0
```

Markdown:

```markdown
# Config Schema Guard Report

## Summary

- Passed checks: 7
- Warnings: 0
- Errors: 5
```

JSON:

```json
{
  "tool": "config-schema-guard",
  "version": "0.1.0",
  "summary": {
    "passed": 7,
    "warnings": 0,
    "errors": 5
  },
  "results": []
}
```

## Sensitive field handling

Values are not shown when a field is marked with `sensitive: true` or when the field path contains `password`, `secret`, `token`, `key`, `cookie`, or `credential`.

Use `--no-values` to omit all config values from reports. This is recommended when saving reports, sharing reports, or running in logs that other people may read.

This tool is not a secret scanner and does not promise to find all sensitive data.

## Exit codes

- `0`: no validation errors.
- `1`: one or more validation errors.
- `2`: CLI usage, loading, or schema parsing error.

Warnings do not fail the command in v0.1.

## Examples directory

- `examples/schema/basic.schema.json`: sample v1 schema.
- `examples/good-config/config.json`: JSON config expected to pass.
- `examples/good-config/config.toml`: TOML config expected to pass.
- `examples/bad-config/config.json`: JSON config expected to fail validation.
- `examples/bad-config/config.toml`: TOML config expected to fail validation.

All example sensitive values are fake placeholders.

## Running tests

```bash
python -m pytest
```

## GitHub Actions and CI

The included workflow tests Python 3.11 and 3.12, installs the package with development dependencies, runs pytest, and checks the example configs. The bad example is expected to return exit code `1`; the workflow verifies that behavior without failing the whole CI job.

## Roadmap

See [ROADMAP.md](ROADMAP.md). The first public version focuses on JSON/TOML loading, simple schema validation, redacted reports, CLI behavior, tests, and docs.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New validation rules should include tests, docs updates, and conservative wording around security and privacy claims.

## Contributors

- s23asd321-del: project owner and maintainer
- OpenAI Codex: AI-assisted development support.

## Security

See [SECURITY.md](SECURITY.md). Do not paste real private config files, real secrets, or real logs into public issues.

## Privacy

See [PRIVACY.md](PRIVACY.md). The tool is local-first, does not upload files, and does not collect telemetry by default.

## Disclaimer

See [DISCLAIMER.md](DISCLAIMER.md). This project provides configuration structure checks only. It is not legal advice, a security audit, a vulnerability scanner, a secret scanner, or proof that a configuration is correct.

## License

MIT License. See [LICENSE](LICENSE).
