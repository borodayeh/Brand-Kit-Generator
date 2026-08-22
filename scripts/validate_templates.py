#!/usr/bin/env python3
"""Validate every bundled template against structure.schema.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from brand_kit_generator import cli  # noqa: E402


def main() -> int:
    try:
        import jsonschema
    except ImportError:
        print("jsonschema is not installed: pip install jsonschema")
        return 1

    schema = json.loads(cli.SCHEMA_FILE.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    failed = False
    for name, path in cli.available_templates().items():
        data = json.loads(path.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(data), key=lambda e: list(e.path))
        if errors:
            failed = True
            print(f"✗ {name}")
            for error in errors:
                location = "/".join(str(p) for p in error.path) or "<root>"
                print(f"    {location}: {error.message}")
        else:
            nodes, _ = cli.split_meta(data)
            cli.validate_structure(nodes)
            print(f"✓ {name}")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
