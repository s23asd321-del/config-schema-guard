# Security and Privacy

config-schema-guard is designed to process local files.

## Local processing

The CLI reads a local schema file and a local config file. It does not execute configuration content.

## No network by default

The first version does not make network requests, fetch remote schemas, upload files, or collect telemetry.

## Sensitive values

Values are omitted when a field is marked `sensitive: true` or when the field path contains sensitive-looking terms such as `password`, `secret`, `token`, `key`, `cookie`, or `credential`.

Use `--no-values` when report output may be stored or shared.

## Not a replacement for security tooling

This project is not a secret scanner, vulnerability scanner, security audit, or privacy compliance tool. It may miss issues and may report issues that are not relevant in a specific project.

