# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog, and this project aims to follow semantic versioning after the schema and CLI stabilize.

## [Unreleased]

### Added

- Initial lightweight schema validation CLI.
- JSON and TOML config loading.
- JSON and TOML schema loading.
- Text, Markdown, and JSON reports.
- Sensitive field redaction.
- Example schema and configs.
- Pytest coverage and GitHub Actions CI.
- Lightweight array item, array length, and object child rules.
- Ruff, mypy, and coverage configuration.
- CLI `--version` output.
- PEP 561 `py.typed` marker for typed package consumers.

### Changed

- `--output` now refuses to overwrite existing files unless `--force` is used.
- CI now checks Python 3.11, 3.12, and 3.13.

### Fixed

- Nothing yet.

### Security

- Reports redact fields marked sensitive and fields with sensitive-looking names.
