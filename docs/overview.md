# Overview

config-schema-guard is a local-first CLI for checking whether JSON and TOML configuration files follow a small schema file.

## Background

Many small tools have example configs that drift over time. A config may miss a required field, use a string where an integer is expected, or contain a value outside a documented list. These issues often appear only when the tool starts.

This project adds a lightweight pre-check for those cases.

## Target users

- Developers maintaining small tools.
- Open source maintainers with example configs.
- CI users who want example config checks.
- Teachers and learners who need a readable validation example.

## Non-target users

- Teams needing full JSON Schema compatibility.
- Teams needing policy enforcement, secret scanning, or security audits.
- Users needing remote config management.
- Users needing YAML support in the first version.

## Typical scenarios

- Validate `config.example.json` in CI.
- Check a local `config.toml` before running a tool.
- Keep teaching examples aligned with docs.
- Demonstrate simple schema-driven validation.

## When to choose something else

Use JSON Schema and a mature validator when you need a standard schema language, cross-language compatibility, complex conditional validation, deep nested object constraints, or formal API contract validation.
