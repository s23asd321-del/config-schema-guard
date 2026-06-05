# Tests

The test suite covers:

- JSON and TOML loading.
- Schema loading and validation.
- Rule validation.
- Sensitive value redaction.
- Text, Markdown, and JSON reports.
- CLI behavior and exit codes.
- Example config behavior.
- Conservative report file overwrite behavior.
- Lightweight array and object rules.

Run:

```bash
python -m pytest
python -m ruff check .
python -m mypy
python -m coverage run -m pytest
python -m coverage report
```
