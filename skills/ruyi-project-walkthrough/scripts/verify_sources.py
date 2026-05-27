#!/usr/bin/env python3
"""
sources-manifest.json 验证脚本

检查 walkthrough 产出的 sources-manifest.json 是否合法，
以及 manifest 中引用的源文件是否真实存在。

用法：
  python scripts/verify_sources.py examples/bat docs/sources-manifest.json
  python scripts/verify_sources.py examples/bat docs/sources-manifest.json --source-dir examples/_src_bat
  python scripts/verify_sources.py --check-all examples/            # 检查所有项目
"""

import json
import re
import sys
import argparse
from pathlib import Path

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    jsonschema = None
    HAS_JSONSCHEMA = False

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
SCHEMA_PATH = PROJECT_ROOT / "docs" / "sources-manifest.schema.json"

CLAIM_ID_PATTERN = re.compile(r"^claim-\d{3,}$")
REQUIRED_TOP_KEYS = {"schema_version", "source_project", "generated_at", "claims"}
REQUIRED_CLAIM_KEYS = {"id", "type", "source_file", "claim_summary", "verified"}
FINAL_REQUIRED_KEYS = {"id", "type", "source_file", "claim_summary", "verified", "doc_file", "doc_line"}
VALID_CLAIM_TYPES = {
    "code_example", "directory_structure", "api_signature",
    "version_number", "architecture_claim", "dependency_claim",
    "config_claim", "feature_claim", "performance_claim",
}
REQUIRED_UNVERIFIED_KEYS = {"id", "claim_summary", "reason"}


class VerificationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    @property
    def ok(self):
        return len(self.errors) == 0

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)

    def report(self):
        lines = []
        if self.errors:
            lines.append(f"ERRORS ({len(self.errors)}):")
            for e in self.errors:
                lines.append(f"  ✗ {e}")
        if self.warnings:
            lines.append(f"WARNINGS ({len(self.warnings)}):")
            for w in self.warnings:
                lines.append(f"  ⚠ {w}")
        if self.ok and not self.warnings:
            lines.append("  ✓ All checks passed")
        elif self.ok:
            lines.append(f"  ✓ Passed with {len(self.warnings)} warning(s)")
        return "\n".join(lines)


def load_schema():
    if not SCHEMA_PATH.exists():
        return None
    try:
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Warning: Schema file is invalid JSON: {e}")
        return None


def validate_basic(manifest, result, strict=False):
    """基础验证：不依赖 jsonschema.

    strict=True: 要求 doc_file/doc_line（最终态验证）
    strict=False: doc_file/doc_line 可选（Phase 3A 中间态）
    """
    for key in REQUIRED_TOP_KEYS:
        if key not in manifest:
            result.error(f"Missing required top-level key: {key}")

    if "schema_version" in manifest and manifest["schema_version"] != "1.0":
        result.error(f"Unsupported schema_version: {manifest.get('schema_version')}")

    sp = manifest.get("source_project", {})
    if not sp.get("name"):
        result.error("source_project.name is required")

    claims = manifest.get("claims", [])
    if not isinstance(claims, list):
        result.error("claims must be an array")
        return

    if len(claims) == 0:
        result.warn("claims array is empty — no claims verified")

    claim_ids = set()
    required_keys = FINAL_REQUIRED_KEYS if strict else REQUIRED_CLAIM_KEYS

    for i, claim in enumerate(claims):
        prefix = f"claims[{i}]"

        for key in required_keys:
            if key not in claim:
                label = "required (final)" if strict else "required"
                result.error(f"{prefix}: missing {label} key: {key}")

        cid = claim.get("id", f"(index {i})")
        if not CLAIM_ID_PATTERN.match(str(cid)):
            result.error(f"{prefix}: invalid claim id format: {cid!r} (expected claim-NNN, 3+ digits)")
        if cid in claim_ids:
            result.error(f"{prefix}: duplicate claim id: {cid}")
        claim_ids.add(cid)

        ctype = claim.get("type")
        if ctype and ctype not in VALID_CLAIM_TYPES:
            result.error(f"{prefix}: invalid claim type: {ctype}")

        doc_line = claim.get("doc_line")
        if doc_line is not None and doc_line < 1:
            result.error(f"{prefix}: doc_line must be >= 1, got {doc_line}")

        source_lines = claim.get("source_lines")
        if source_lines is not None:
            if not isinstance(source_lines, list):
                result.error(f"{prefix}: source_lines must be an array or null")
            elif len(source_lines) != 2:
                result.error(f"{prefix}: source_lines must have exactly 2 elements, got {len(source_lines)}")
            elif source_lines[0] > source_lines[1]:
                result.error(f"{prefix}: source_lines start > end: {source_lines}")
            elif source_lines[0] < 1:
                result.error(f"{prefix}: source_lines must be >= 1")

        if not strict and "doc_file" not in claim:
            result.warn(f"{prefix}: doc_file not set (expected in Phase 3B)")

    unverified = manifest.get("unverified", [])
    if not isinstance(unverified, list):
        result.error("unverified must be an array")
        return

    for i, uv in enumerate(unverified):
        prefix = f"unverified[{i}]"
        for key in REQUIRED_UNVERIFIED_KEYS:
            if key not in uv:
                result.error(f"{prefix}: missing required key: {key}")

    if len(unverified) > 0:
        result.warn(f"{len(unverified)} unverifiable claims: {[uv.get('reason', '?') for uv in unverified]}")


def validate_jsonschema(manifest, schema, result):
    if not HAS_JSONSCHEMA or jsonschema is None:
        result.warn("jsonschema not installed, skipping schema validation (pip install jsonschema)")
        return
    try:
        jsonschema.validate(manifest, schema)
    except jsonschema.ValidationError as e:
        result.error(f"Schema validation: {e.message}")


def validate_source_files(manifest, source_dir, result):
    if not source_dir or not source_dir.exists():
        return

    claims = manifest.get("claims", [])
    checked = 0
    missing = 0

    for claim in claims:
        source_file = claim.get("source_file")
        if not source_file:
            continue

        source_path = source_dir / source_file
        checked += 1

        if not source_path.exists():
            result.error(f"claim {claim.get('id', '?')}: source file not found: {source_file}")
            missing += 1
            continue

        source_lines = claim.get("source_lines")
        if source_lines:
            with open(source_path, "r", encoding="utf-8", errors="replace") as sf:
                total_lines = sum(1 for _ in sf)
            if source_lines[1] > total_lines:
                result.error(
                    f"claim {claim.get('id', '?')}: source_lines {source_lines} "
                    f"exceeds file length ({total_lines} lines): {source_file}"
                )

    if checked > 0:
        result.info.append(f"Checked {checked} source files, {missing} missing")


def validate_manifest(manifest_path, source_dir=None, strict=False):
    manifest_path = Path(manifest_path)
    result = VerificationResult()

    if not manifest_path.exists():
        result.error(f"Manifest file not found: {manifest_path}")
        return result

    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        result.error(f"Invalid JSON: {e}")
        return result

    schema = load_schema()
    if schema:
        validate_jsonschema(manifest, schema, result)

    validate_basic(manifest, result, strict=strict)
    validate_source_files(manifest, source_dir, result)

    return result


def find_manifests(examples_dir):
    examples_dir = Path(examples_dir)
    manifests = []

    for project_dir in sorted(examples_dir.iterdir()):
        if not project_dir.is_dir() or project_dir.name.startswith("_"):
            continue

        brief_manifest = project_dir / "docs" / "sources-manifest.json"
        if brief_manifest.exists():
            manifests.append((project_dir.name, "brief", brief_manifest))

        medium_manifest = project_dir / "docs" / "medium" / "sources-manifest.json"
        if medium_manifest.exists():
            manifests.append((project_dir.name, "medium", medium_manifest))

        deep_manifest = project_dir / "docs" / "deep" / "sources-manifest.json"
        if deep_manifest.exists():
            manifests.append((project_dir.name, "deep", deep_manifest))

    return manifests


def main():
    parser = argparse.ArgumentParser(description="Verify sources-manifest.json files")
    parser.add_argument("manifest", nargs="?", help="Path to sources-manifest.json")
    parser.add_argument("--source-dir", help="Path to source project for file existence checks")
    parser.add_argument("--strict", action="store_true",
                        help="Require doc_file/doc_line (final state validation)")
    parser.add_argument("--check-all", metavar="EXAMPLES_DIR",
                        help="Check all manifests under examples directory")
    parser.add_argument("--project", help="Project name (for --check-all, limits to one project)")

    args = parser.parse_args()

    if args.check_all:
        manifests = find_manifests(args.check_all)
        if args.project:
            manifests = [(p, d, f) for p, d, f in manifests if p == args.project]

        if not manifests:
            print("No manifest files found.")
            print("Hint: manifests should be at docs/sources-manifest.json in each project directory.")
            sys.exit(1)

        total_ok = 0
        total_fail = 0
        for project, depth, manifest_path in manifests:
            source_dir = Path(args.check_all) / f"_src_{project}"
            print(f"\n{'='*60}")
            print(f"Project: {project} | Depth: {depth}")
            print(f"Manifest: {manifest_path}")
            print(f"{'='*60}")

            result = validate_manifest(manifest_path, source_dir, strict=args.strict)
            print(result.report())

            if result.ok:
                total_ok += 1
            else:
                total_fail += 1

        print(f"\n{'='*60}")
        print(f"Summary: {total_ok} passed, {total_fail} failed, {total_ok + total_fail} total")
        sys.exit(0 if total_fail == 0 else 1)

    elif args.manifest:
        source_dir = Path(args.source_dir) if args.source_dir else None
        result = validate_manifest(args.manifest, source_dir, strict=args.strict)
        print(result.report())
        sys.exit(0 if result.ok else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
