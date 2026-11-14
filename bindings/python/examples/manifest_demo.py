#!/usr/bin/env python3
"""Validate a versioned JSON manifest and optionally inspect it with Tokenizers.

This is a runnable example, not a financial, KYC, legal, or compliance decision engine.
Tokenization is text processing only: token IDs do not validate or authorize a manifest.

Examples:
    python manifest_demo.py --demo
    python manifest_demo.py manifest.json --expected-version 2026.11.02-sovereign-v1
    python manifest_demo.py --demo --tokenizer path/to/tokenizer.json
    python manifest_demo.py --self-test
"""

from __future__ import annotations

import argparse
import json
import sys
import unittest
from pathlib import Path
from typing import Any

DEMO_MANIFEST: dict[str, Any] = {
    "tenant_id": "northside_retail_001",
    "manifest_version": "2026.11.02-sovereign-v1",
    "status": "AWAITING_PAYMENT",
    "distress_score": 92,
}


def validate_manifest(value: Any, expected_version: str | None = None) -> list[str]:
    """Return structural/version errors; never infer compliance or financial risk."""
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["Manifest must be a JSON object."]

    tenant_id = value.get("tenant_id")
    if not isinstance(tenant_id, str) or not tenant_id.strip():
        errors.append("tenant_id must be a non-empty string.")

    version = value.get("manifest_version")
    if not isinstance(version, str) or not version.strip():
        errors.append("manifest_version must be a non-empty string.")
    elif expected_version is not None and version != expected_version:
        errors.append(f"Unsupported manifest_version: expected {expected_version!r}.")

    status = value.get("status")
    if status is not None and not isinstance(status, str):
        errors.append("status must be a string when provided.")

    score = value.get("distress_score")
    if score is not None and (isinstance(score, bool) or not isinstance(score, (int, float))):
        errors.append("distress_score must be numeric when provided; this tool does not interpret it.")

    return errors


def load_json(path: Path) -> Any:
    try:
        with path.open(encoding="utf-8") as source:
            return json.load(source)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON at line {error.lineno}, column {error.colno}: {error.msg}") from error


def inspect_with_tokenizer(value: dict[str, Any], tokenizer_path: Path) -> dict[str, Any]:
    """Tokenize canonical JSON with this repo's existing Python binding API."""
    try:
        from tokenizers import Tokenizer
    except ImportError as error:
        raise RuntimeError(
            "Tokenizer inspection requires this repository's Python binding to be installed. "
            "See bindings/python/README.md."
        ) from error

    tokenizer = Tokenizer.from_file(str(tokenizer_path)).compile()
    canonical_json = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    encoding = tokenizer.encode(canonical_json)
    return {
        "token_count": len(encoding.ids),
        "ids": encoding.ids,
        "tokens": tokenizer.decode_tokens(encoding.ids),
    }


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("manifest", nargs="?", type=Path, help="Path to a JSON manifest")
    parser.add_argument("--demo", action="store_true", help="Run the included sample manifest")
    parser.add_argument("--expected-version", help="Optional exact manifest version to require")
    parser.add_argument("--tokenizer", type=Path, help="Optional local tokenizer.json for token inspection")
    parser.add_argument("--self-test", action="store_true", help="Run standard-library unit tests")
    return parser


class ManifestValidationTests(unittest.TestCase):
    def test_demo_manifest_is_structurally_valid(self) -> None:
        self.assertEqual(validate_manifest(DEMO_MANIFEST), [])

    def test_expected_version_mismatch_is_reported(self) -> None:
        errors = validate_manifest(DEMO_MANIFEST, "different-version")
        self.assertEqual(len(errors), 1)
        self.assertIn("Unsupported manifest_version", errors[0])

    def test_missing_tenant_is_reported(self) -> None:
        errors = validate_manifest({"manifest_version": "v1"})
        self.assertTrue(any("tenant_id" in error for error in errors))

    def test_non_object_is_rejected(self) -> None:
        self.assertEqual(validate_manifest(["not", "an", "object"]), ["Manifest must be a JSON object."])

    def test_boolean_is_not_accepted_as_numeric_score(self) -> None:
        payload = {**DEMO_MANIFEST, "distress_score": True}
        self.assertTrue(any("distress_score must be numeric" in error for error in validate_manifest(payload)))


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    if args.self_test:
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(ManifestValidationTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1

    if args.demo == (args.manifest is not None):
        print("Choose exactly one input: --demo or a manifest.json path.", file=sys.stderr)
        return 2

    try:
        manifest = DEMO_MANIFEST if args.demo else load_json(args.manifest)
        errors = validate_manifest(manifest, args.expected_version)
        report: dict[str, Any] = {
            "valid_structure": not errors,
            "errors": errors,
            "note": "Structural validation only; this does not establish legal, KYC, payment, or financial compliance.",
        }
        if isinstance(manifest, dict):
            report["manifest"] = manifest
            if args.tokenizer is not None:
                report["tokenization"] = inspect_with_tokenizer(manifest, args.tokenizer)
        elif args.tokenizer is not None:
            report["tokenization_error"] = "Tokenizer inspection requires a JSON object manifest."

        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if not errors else 1
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
