# Design

config-schema-guard keeps the first version small and explicit.

## Module structure

- `loader.py`: loads JSON and TOML files from local disk.
- `schema.py`: loads and validates the schema JSON or TOML file.
- `validator.py`: applies schema rules to a loaded config dictionary.
- `redaction.py`: decides whether a field value should be omitted from reports.
- `report.py`: renders text, Markdown, and JSON reports.
- `cli.py`: parses command-line arguments and maps validation errors to exit codes.
- `models.py`: defines shared dataclasses and severity values.

## Data flow

1. CLI receives a config path and schema path.
2. Schema loader parses the schema JSON or TOML and checks its structure.
3. Config loader parses the JSON or TOML config.
4. Validator reads configured dot paths and applies rules.
5. Redaction marks sensitive values before rendering.
6. Reporter renders the selected output format.
7. CLI exits with `0`, `1`, or `2`.

## Why JSON and TOML only?

Python 3.11 includes `json` and `tomllib` in the standard library. Supporting only these formats keeps v0.1 dependency-light and avoids adding PyYAML.

The same reasoning applies to schema files: JSON schemas are portable, and TOML schemas are more comfortable for TOML-first projects. YAML support may be considered later, but it is intentionally out of scope for the first version.

## Rule design

Rules stay deliberately shallow. Arrays can check whole-array length and a single `items.type`; objects can require immediate child names with `required_children`. More expressive nested object and array validation belongs in mature schema systems such as JSON Schema.
