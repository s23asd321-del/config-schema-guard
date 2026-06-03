from __future__ import annotations

from config_schema_guard.redaction import is_sensitive_field
from config_schema_guard.validator import validate_config


def test_schema_sensitive_true_marks_value_redacted():
    schema = {
        "version": 1,
        "fields": {
            "auth.value": {
                "required": True,
                "type": "string",
                "sensitive": True,
            }
        },
    }

    results = validate_config({"auth": {"value": "SHOULD_NOT_APPEAR"}}, schema)

    assert results[0].value_redacted is True


def test_sensitive_field_name_parts_are_detected():
    for field in (
        "auth.token",
        "db.password",
        "service.secret",
        "service.api_key",
        "session.cookie",
        "client.credential",
    ):
        assert is_sensitive_field(field)


def test_token_password_secret_key_cookie_fields_are_auto_redacted():
    schema = {
        "version": 1,
        "fields": {
            "auth.token": {"required": True, "type": "string"},
            "db.password": {"required": True, "type": "string"},
            "service.secret": {"required": True, "type": "string"},
            "service.api_key": {"required": True, "type": "string"},
            "session.cookie": {"required": True, "type": "string"},
        },
    }
    config = {
        "auth": {"token": "SHOULD_NOT_APPEAR"},
        "db": {"password": "SHOULD_NOT_APPEAR"},
        "service": {"secret": "SHOULD_NOT_APPEAR", "api_key": "SHOULD_NOT_APPEAR"},
        "session": {"cookie": "SHOULD_NOT_APPEAR"},
    }

    results = validate_config(config, schema)

    assert all(item.value_redacted for item in results)

