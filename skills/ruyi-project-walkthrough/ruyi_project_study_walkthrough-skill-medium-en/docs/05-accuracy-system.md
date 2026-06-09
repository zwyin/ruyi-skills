# Accuracy System: Manifest-First Verification

The project's most distinctive feature is its manifest-first accuracy system. Before any chapter content is written, every factual claim must be verified against the actual source code and recorded in `sources-manifest.json`. This chapter explains how that system works.

## Why Manifest-First?

Early versions of the plugin produced walkthroughs with plausible-sounding but fabricated details — wrong line numbers, invented function names, incorrect directory structures. The root cause was that content was written first and verified after (or never).

The manifest-first approach flips this: verification happens **before** writing. The manifest is a **write permit**, not an audit log. If a claim isn't in the manifest with `verified: true`, it cannot appear in the walkthrough.

## Sources Manifest Schema

The manifest follows a JSON Schema defined in `docs/sources-manifest.schema.json`:

```json
// Simplified from: docs/sources-manifest.schema.json:1-7
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "SourcesManifest",
  "description": "Maps walkthrough claims to source project locations...",
  "type": "object",
  "required": ["schema_version", "source_project", "generated_at", "claims"],
  "additionalProperties": false
}
```

### Claim Types

Nine types of claims can be recorded:

| Type | What It Verifies | Example |
|------|-----------------|---------|
| `code_example` | Code block from actual source | Function implementation |
| `directory_structure` | Directory listing | `ls` output |
| `api_signature` | Function/method definition | Parameters, return type |
| `version_number` | Version from config file | package.json version |
| `architecture_claim` | Module interaction | "X imports Y" |
| `dependency_claim` | Import statement | `from X import Y` |
| `config_claim` | Configuration value | Default settings |
| `feature_claim` | Feature existence | CLI flag support |
| `performance_claim` | Performance characteristic | Benchmark results |

### Claim Entry Structure

Each claim has required fields:

```json
// Simplified from: docs/sources-manifest.schema.json:59-126
{
  "id": "claim-001",
  "type": "code_example",
  "source_file": "src/main.py",
  "source_lines": [10, 25],
  "claim_summary": "Main entry point function",
  "verified": true,
  "verification_note": "exact match",
  "doc_file": "01-overview.md",
  "doc_line": 42
}
```

The `source_lines` field is `[start, end]` (1-based, inclusive). For directory-level claims it can be `null`.

## Verification Pipeline

The `verify_sources.py` script (315 lines) implements a three-stage validation:

```python
// Simplified from: scripts/verify_sources.py:87-100
def validate_basic(manifest, result, strict=False):
    """Basic validation: no jsonschema dependency needed.

    strict=True: require doc_file/doc_line (final state)
    strict=False: doc_file/doc_line optional (Phase 3A intermediate)
    """
    for key in REQUIRED_TOP_KEYS:
        if key not in manifest:
            result.error(f"Missing required top-level key: {key}")

    if "schema_version" in manifest and manifest["schema_version"] != "1.0":
        result.error(f"Unsupported schema_version: ...")
```

### Stage 1: Basic Validation

Checks required keys, claim ID format (`claim-NNN` with 3+ digits), claim types, duplicate IDs, and line range validity (start <= end, both >= 1).

### Stage 2: JSON Schema Validation

If the `jsonschema` package is installed, validates the full manifest against `docs/sources-manifest.schema.json`. This catches structural issues like unknown properties or missing required fields.

### Stage 3: Source File Verification

```python
// Simplified from: scripts/verify_sources.py:177-206
def validate_source_files(manifest, source_dir, result):
    for claim in claims:
        source_path = source_dir / source_file
        if not source_path.exists():
            result.error(f"source file not found: {source_file}")
            continue
        source_lines = claim.get("source_lines")
        if source_lines:
            total_lines = sum(1 for _ in sf)
            if source_lines[1] > total_lines:
                result.error(f"source_lines exceeds file length")
```

This stage confirms that every referenced source file actually exists and that line ranges don't exceed file bounds.

## VerificationResult

The script uses a `VerificationResult` class to collect errors, warnings, and info messages:

```python
// Simplified from: scripts/verify_sources.py:43-73
class VerificationResult:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []

    @property
    def ok(self):
        return len(self.errors) == 0

    def report(self):
        if self.errors:
            lines.append(f"ERRORS ({len(self.errors)}):")
            for e in self.errors:
                lines.append(f"  ✗ {e}")
        if self.ok and not self.warnings:
            lines.append("  ✓ All checks passed")
```

Errors block delivery. Warnings are informational. The `ok` property is `True` only when there are zero errors.

## CLI Usage

```bash
# Verify a single manifest
python scripts/verify_sources.py docs/sources-manifest.json --source-dir ../..

# Verify all manifests in examples/
python scripts/verify_sources.py --check-all examples/

# Strict mode (requires doc_file/doc_line)
python scripts/verify_sources.py docs/sources-manifest.json --strict
```

The `--strict` flag requires `doc_file` and `doc_line` fields on every claim, used in Phase 3C (final validation after content is written).

[Previous: Converter Engine](04-converter-engine.md) | [Next: Dependency Graph](06-dependency-graph.md)
