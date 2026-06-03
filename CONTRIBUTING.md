# Contributing

Thank you for considering a contribution.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m pytest
```

## Guidelines

- Keep the first version local-first and dependency-light.
- Add tests for new validation behavior.
- Update README or docs for user-visible changes.
- Avoid broad security, privacy, or compliance claims.
- Do not add real secrets or private configuration data to examples, tests, issues, or docs.
- Do not introduce network calls, AI SDKs, databases, Web UI, or plugin systems without a documented project decision.

## Pull requests

Before opening a pull request, run `python -m pytest` and check that examples contain only fake placeholder values.

