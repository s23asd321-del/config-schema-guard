# Release Checklist

Before a release:

- `python -m pytest` passes.
- `python -m ruff check .` passes.
- `python -m mypy` passes.
- `python -m coverage run -m pytest` and `python -m coverage report` pass.
- CLI examples pass.
- README is updated.
- CHANGELOG is updated.
- Examples contain no real sensitive information.
- Docs avoid overclaiming security, privacy, or compliance capabilities.
- GitHub Actions is passing.
- The repository does not contain `.venv`, `__pycache__`, `.pytest_cache`, `dist`, `build`, or `*.egg-info`.
- Consider enabling GitHub Dependabot, secret scanning, push protection, and code scanning if the repository or account supports them.
