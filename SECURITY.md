# Security Policy

## Reporting security issues

Please report security concerns privately through the repository maintainer contact method once one is published. Until then, avoid posting sensitive details in public issues.

Do not include real private configuration files, real secrets, real tokens, real logs, real cookies, real passwords, real API keys, or private infrastructure details in public reports.

## Scope

config-schema-guard is not a secret scanner, vulnerability scanner, security audit tool, or proof that a configuration is safe.

The tool checks selected structure rules in local JSON and TOML files. It may produce false positives and false negatives.

## Sensitive values

Sensitive fields should be redacted by default when fields are marked `sensitive: true` or when field names look sensitive. Use `--no-values` when producing reports that may be shared.

