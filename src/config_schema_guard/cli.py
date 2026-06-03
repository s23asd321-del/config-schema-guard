"""Command-line interface for config-schema-guard."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from config_schema_guard.loader import ConfigLoadError, load_config
from config_schema_guard.report import build_report, render_report
from config_schema_guard.schema import SchemaError, load_schema
from config_schema_guard.validator import validate_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="config-guard",
        description="Validate JSON and TOML config files against a lightweight schema.",
    )
    subparsers = parser.add_subparsers(dest="command")

    check = subparsers.add_parser("check", help="Validate a config file.")
    check.add_argument("config_path", help="Path to a JSON or TOML config file.")
    check.add_argument(
        "--schema",
        required=True,
        help="Path to a config-schema-guard schema JSON file.",
    )
    check.add_argument(
        "--format",
        choices=("text", "markdown", "json"),
        default="text",
        help="Report output format.",
    )
    check.add_argument("--output", help="Optional path to write the report.")
    check.add_argument(
        "--strict",
        action="store_true",
        help="Warn about fields that are not declared in the schema.",
    )
    check.add_argument(
        "--no-values",
        action="store_true",
        help="Do not include config values in reports.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        return _run_check(args)

    parser.error("a command is required")
    return 2


def _run_check(args: argparse.Namespace) -> int:
    try:
        schema = load_schema(args.schema)
        config = load_config(args.config_path)
        results = validate_config(
            config,
            schema,
            strict=args.strict,
            no_values=args.no_values,
        )
        report = build_report(
            config_path=args.config_path,
            schema_path=args.schema,
            results=results,
        )
        rendered = render_report(
            report,
            output_format=args.format,
            include_values=not args.no_values,
        )

        if args.output:
            output_path = Path(args.output)
            output_path.write_text(rendered + "\n", encoding="utf-8")
        else:
            print(rendered)

        return 1 if report.has_errors else 0
    except (ConfigLoadError, SchemaError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

