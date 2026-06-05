# Schema Format

The v1 schema format can be written as JSON or TOML. In both formats it contains a `version` and a `fields` object/table.

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
- `items`: object with `type`, used for lightweight array item type checks.
- `min_items`: minimum array length.
- `max_items`: maximum array length.
- `required_children`: list of immediate child field names required inside an object.
- `sensitive`: boolean. Sensitive values are omitted from reports.
- `description`: string used for documentation and report context.

## Rule compatibility checks

Schema files are checked before config validation starts:

- `min` must be less than or equal to `max`.
- `min_length` must be less than or equal to `max_length`.
- `min_items` must be less than or equal to `max_items`.
- `min` and `max` require `type` to be `integer` or `number`.
- `min_length` and `max_length` require `type` to be `string`.
- `items`, `min_items`, and `max_items` require `type` to be `array`.
- `required_children` requires `type` to be `object`.
- `allowed` values must match the declared `type` when a type is declared.

## TOML schema example

```toml
version = 1
name = "basic app config"

[fields."server.port"]
required = true
type = "integer"
min = 1
max = 65535

[fields.labels]
required = false
type = "array"
min_items = 1
max_items = 10

[fields.labels.items]
type = "string"

[fields.metadata]
required = false
type = "object"
required_children = ["owner"]
```

## Limitations

- No YAML support in v0.1.
- No remote URL loading.
- No array index paths. Array support is limited to whole-array checks and simple `items.type`.
- No nested object schema blocks. Use dot paths or `required_children` for small object checks.
- No conditional rules.
- No automatic fixes.
- No full JSON Schema compatibility.

## Difference from JSON Schema

This format is smaller and intentionally less expressive. It is designed for readable project-local checks, not for broad validation interoperability. Use JSON Schema when you need a mature standard, validators across languages, or advanced schema features.
