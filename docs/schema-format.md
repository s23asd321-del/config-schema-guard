# Schema Format

The v1 schema format is a JSON object with a `version` and a `fields` object.

```json
{
  "version": 1,
  "name": "basic app config",
  "fields": {
    "server.port": {
      "required": true,
      "type": "integer",
      "min": 1,
      "max": 65535
    }
  }
}
```

## Field paths

Fields use dot paths such as `app.name` or `server.port`. The first version supports nested dictionaries but does not support array index paths.

## Supported rules

- `required`: boolean. Missing required fields produce errors.
- `type`: one of `string`, `integer`, `number`, `boolean`, `array`, or `object`.
- `allowed`: list of accepted values.
- `min`: numeric minimum.
- `max`: numeric maximum.
- `min_length`: minimum string length.
- `max_length`: maximum string length.
- `sensitive`: boolean. Sensitive values are omitted from reports.
- `description`: string used for documentation and report context.

## Limitations

- No YAML support in v0.1.
- No remote URL loading.
- No array index paths.
- No conditional rules.
- No automatic fixes.
- No full JSON Schema compatibility.

## Difference from JSON Schema

This format is smaller and intentionally less expressive. It is designed for readable project-local checks, not for broad validation interoperability. Use JSON Schema when you need a mature standard, validators across languages, or advanced schema features.

