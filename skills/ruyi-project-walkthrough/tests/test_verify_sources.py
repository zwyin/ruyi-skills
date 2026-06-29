"""
Unit tests for scripts/verify_sources.py

Covers VerificationResult, validate_basic (strict and non-strict),
validate_source_files, find_manifests, validate_manifest, and load_schema.
"""

import json
import sys
import pytest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.verify_sources import (
    VerificationResult,
    validate_basic,
    validate_source_files,
    validate_manifest,
    find_manifests,
    load_schema,
    SCHEMA_PATH,
    CLAIM_ID_PATTERN,
    REQUIRED_TOP_KEYS,
    REQUIRED_CLAIM_KEYS,
    FINAL_REQUIRED_KEYS,
    VALID_CLAIM_TYPES,
    REQUIRED_UNVERIFIED_KEYS,
)


# ─── Helpers ────────────────────────────────────────────────────


def _make_minimal_manifest(**overrides):
    """Return a valid minimal manifest (non-strict mode).

    Uses 'repo_url' (not 'url') to match the JSON schema's allowed fields.
    """
    manifest = {
        "schema_version": "1.0",
        "source_project": {"name": "test-project", "repo_url": "https://example.com"},
        "generated_at": "2025-01-01T00:00:00Z",
        "claims": [
            {
                "id": "claim-001",
                "type": "code_example",
                "source_file": "src/main.py",
                "claim_summary": "A claim.",
                "verified": True,
            }
        ],
    }
    manifest.update(overrides)
    return manifest


def _make_full_claim(**overrides):
    """Return a claim with all final-required fields."""
    claim = {
        "id": "claim-001",
        "type": "code_example",
        "source_file": "src/main.py",
        "claim_summary": "A claim.",
        "verified": True,
        "doc_file": "docs/walkthrough.md",
        "doc_line": 10,
    }
    claim.update(overrides)
    return claim


def _write_manifest(tmp_path, manifest, filename="sources-manifest.json"):
    """Write manifest JSON to a file under tmp_path and return the path."""
    p = tmp_path / filename
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(manifest), encoding="utf-8")
    return p


# ─── VerificationResult ─────────────────────────────────────────


class TestVerificationResult:
    def test_ok_true_when_empty(self):
        r = VerificationResult()
        assert r.ok is True
        assert r.errors == []
        assert r.warnings == []

    def test_error_adds_to_errors_and_ok_false(self):
        r = VerificationResult()
        r.error("something broke")
        assert len(r.errors) == 1
        assert "something broke" in r.errors[0]
        assert r.ok is False

    def test_warn_adds_to_warnings_and_ok_still_true(self):
        r = VerificationResult()
        r.warn("minor issue")
        assert len(r.warnings) == 1
        assert "minor issue" in r.warnings[0]
        assert r.ok is True

    def test_report_all_checks_passed(self):
        r = VerificationResult()
        report = r.report()
        assert "All checks passed" in report

    def test_report_with_errors(self):
        r = VerificationResult()
        r.error("err1")
        r.error("err2")
        report = r.report()
        assert "ERRORS (2):" in report
        assert "err1" in report
        assert "err2" in report

    def test_report_with_warnings_only(self):
        r = VerificationResult()
        r.warn("w1")
        report = r.report()
        assert "WARNINGS (1):" in report
        assert "Passed with 1 warning(s)" in report

    def test_report_with_errors_and_warnings(self):
        r = VerificationResult()
        r.error("bad")
        r.warn("meh")
        report = r.report()
        assert "ERRORS (1):" in report
        assert "WARNINGS (1):" in report
        # When there are errors, no "Passed" line
        assert "Passed" not in report


# ─── validate_basic — non-strict mode ───────────────────────────


class TestValidateBasicNonStrict:
    def test_valid_minimal_manifest_passes(self):
        r = VerificationResult()
        validate_basic(_make_minimal_manifest(), r)
        assert r.ok is True

    def test_missing_top_level_keys(self):
        manifest = {"schema_version": "1.0"}
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        # Should have errors for each missing required top-level key
        missing = REQUIRED_TOP_KEYS - {"schema_version"}
        for key in missing:
            assert any(key in e for e in r.errors), f"Expected error for missing key '{key}'"

    def test_wrong_schema_version(self):
        manifest = _make_minimal_manifest(schema_version="2.0")
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("schema_version" in e for e in r.errors)

    def test_missing_source_project_name(self):
        manifest = _make_minimal_manifest()
        manifest["source_project"] = {"repo_url": "https://example.com"}
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("source_project.name" in e for e in r.errors)

    def test_claims_not_array(self):
        manifest = _make_minimal_manifest(claims="not a list")
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("claims must be an array" in e for e in r.errors)

    def test_empty_claims_warning(self):
        manifest = _make_minimal_manifest(claims=[])
        r = VerificationResult()
        validate_basic(manifest, r)
        # Empty claims is a warning, not an error
        assert r.ok is True
        assert any("empty" in w for w in r.warnings)

    def test_valid_claim_all_fields_passes(self):
        manifest = _make_minimal_manifest()
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is True
        assert len(r.errors) == 0

    def test_missing_claim_keys(self):
        manifest = _make_minimal_manifest(claims=[{"id": "claim-001"}])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        missing_keys = REQUIRED_CLAIM_KEYS - {"id"}
        for key in missing_keys:
            assert any(key in e for e in r.errors), f"Expected error for missing claim key '{key}'"

    def test_invalid_claim_id_format_c001(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "id": "c-001"}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("invalid claim id" in e for e in r.errors)

    def test_invalid_claim_id_format_claim12(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "id": "claim-12"}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("invalid claim id" in e for e in r.errors)

    def test_invalid_claim_id_format_uppercase(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "id": "CL-001"}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("invalid claim id" in e for e in r.errors)

    def test_valid_claim_id_format(self):
        assert CLAIM_ID_PATTERN.match("claim-001")
        assert CLAIM_ID_PATTERN.match("claim-123")
        assert CLAIM_ID_PATTERN.match("claim-9999")
        assert not CLAIM_ID_PATTERN.match("claim-01")
        assert not CLAIM_ID_PATTERN.match("c-001")

    def test_duplicate_claim_ids(self):
        manifest = _make_minimal_manifest(claims=[
            _make_full_claim(),
            {**_make_full_claim(), "source_file": "other.py"},
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("duplicate claim id" in e for e in r.errors)

    def test_invalid_claim_type(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "type": "invalid_type"}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("invalid claim type" in e for e in r.errors)

    def test_valid_claim_types(self):
        for ctype in VALID_CLAIM_TYPES:
            manifest = _make_minimal_manifest(claims=[
                {**_make_full_claim(), "id": f"claim-{hash(ctype) % 10000:03d}", "type": ctype}
            ])
            r = VerificationResult()
            validate_basic(manifest, r)
            assert r.ok is True, f"claim type '{ctype}' should be valid"

    def test_doc_line_less_than_1(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "doc_line": 0}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("doc_line" in e for e in r.errors)

    def test_doc_line_negative(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "doc_line": -5}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("doc_line" in e for e in r.errors)

    def test_source_lines_not_array(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_lines": "1-10"}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("source_lines must be an array" in e for e in r.errors)

    def test_source_lines_wrong_length(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_lines": [1, 10, 20]}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("exactly 2 elements" in e for e in r.errors)

    def test_source_lines_start_greater_than_end(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_lines": [20, 10]}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("start > end" in e for e in r.errors)

    def test_source_lines_less_than_1(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_lines": [0, 10]}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("source_lines must be >= 1" in e for e in r.errors)

    def test_source_lines_valid(self):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_lines": [1, 10]}
        ])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is True

    def test_missing_doc_file_nonstrict_is_warning(self):
        claim = {
            "id": "claim-001",
            "type": "code_example",
            "source_file": "src/main.py",
            "claim_summary": "A claim.",
            "verified": True,
        }
        manifest = _make_minimal_manifest(claims=[claim])
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is True
        assert any("doc_file" in w for w in r.warnings)

    def test_unverified_missing_required_keys(self):
        manifest = _make_minimal_manifest()
        manifest["unverified"] = [{"id": "claim-999"}]
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        missing = REQUIRED_UNVERIFIED_KEYS - {"id"}
        for key in missing:
            assert any(key in e for e in r.errors), f"Expected error for missing unverified key '{key}'"

    def test_unverified_not_array(self):
        manifest = _make_minimal_manifest()
        manifest["unverified"] = "bad"
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is False
        assert any("unverified must be an array" in e for e in r.errors)

    def test_unverified_entries_present_is_warning(self):
        manifest = _make_minimal_manifest()
        manifest["unverified"] = [
            {"id": "claim-999", "claim_summary": "x", "reason": "file deleted"}
        ]
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is True
        assert any("unverifiable" in w for w in r.warnings)

    def test_unverified_valid_entries_pass(self):
        manifest = _make_minimal_manifest()
        manifest["unverified"] = [
            {"id": "claim-999", "claim_summary": "x", "reason": "file deleted"}
        ]
        r = VerificationResult()
        validate_basic(manifest, r)
        assert r.ok is True


# ─── validate_basic — strict mode ───────────────────────────────


class TestValidateBasicStrict:
    def test_missing_doc_file_strict_is_error(self):
        claim = {
            "id": "claim-001",
            "type": "code_example",
            "source_file": "src/main.py",
            "claim_summary": "A claim.",
            "verified": True,
            "doc_line": 10,
        }
        manifest = _make_minimal_manifest(claims=[claim])
        r = VerificationResult()
        validate_basic(manifest, r, strict=True)
        assert r.ok is False
        assert any("doc_file" in e for e in r.errors)

    def test_missing_doc_line_strict_is_error(self):
        claim = {
            "id": "claim-001",
            "type": "code_example",
            "source_file": "src/main.py",
            "claim_summary": "A claim.",
            "verified": True,
            "doc_file": "docs/walkthrough.md",
        }
        manifest = _make_minimal_manifest(claims=[claim])
        r = VerificationResult()
        validate_basic(manifest, r, strict=True)
        assert r.ok is False
        assert any("doc_line" in e for e in r.errors)

    def test_all_required_keys_present_passes(self):
        manifest = _make_minimal_manifest(claims=[_make_full_claim()])
        r = VerificationResult()
        validate_basic(manifest, r, strict=True)
        assert r.ok is True

    def test_strict_requires_all_final_keys(self):
        """Strict mode checks FINAL_REQUIRED_KEYS, not just REQUIRED_CLAIM_KEYS."""
        assert FINAL_REQUIRED_KEYS > REQUIRED_CLAIM_KEYS
        # The extra keys are doc_file and doc_line
        assert "doc_file" in FINAL_REQUIRED_KEYS - REQUIRED_CLAIM_KEYS
        assert "doc_line" in FINAL_REQUIRED_KEYS - REQUIRED_CLAIM_KEYS


# ─── validate_source_files ──────────────────────────────────────


class TestValidateSourceFiles:
    def test_source_dir_does_not_exist_silently_skips(self, tmp_path):
        manifest = _make_minimal_manifest()
        r = VerificationResult()
        validate_source_files(manifest, tmp_path / "nonexistent", r)
        assert r.ok is True
        assert len(r.warnings) == 0

    def test_source_dir_is_none_silently_skips(self):
        manifest = _make_minimal_manifest()
        r = VerificationResult()
        validate_source_files(manifest, None, r)
        assert r.ok is True
        assert len(r.warnings) == 0

    def test_source_file_not_found_is_error(self, tmp_path):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_file": "nonexistent.py"}
        ])
        r = VerificationResult()
        validate_source_files(manifest, tmp_path, r)
        assert r.ok is False
        assert any("source file not found" in e for e in r.errors)

    def test_source_lines_exceed_file_length(self, tmp_path):
        src_file = tmp_path / "src"
        src_file.mkdir()
        (src_file / "main.py").write_text("line1\nline2\nline3\n", encoding="utf-8")
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_file": "main.py", "source_lines": [1, 100]}
        ])
        r = VerificationResult()
        validate_source_files(manifest, src_file, r)
        assert r.ok is False
        assert any("exceeds file length" in e for e in r.errors)

    def test_source_lines_within_file_length_passes(self, tmp_path):
        src_file = tmp_path / "src"
        src_file.mkdir()
        (src_file / "main.py").write_text("line1\nline2\nline3\n", encoding="utf-8")
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_file": "main.py", "source_lines": [1, 3]}
        ])
        r = VerificationResult()
        validate_source_files(manifest, src_file, r)
        assert r.ok is True

    def test_claim_without_source_file_skipped(self, tmp_path):
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_file": ""}
        ])
        r = VerificationResult()
        validate_source_files(manifest, tmp_path, r)
        assert r.ok is True
        assert len(r.errors) == 0

    def test_directory_claim_with_source_lines_does_not_crash(self, tmp_path):
        """Regression: a directory_structure claim whose source_file is a real
        directory must not raise IsADirectoryError when source_lines is present.
        (Bug 2 — the verifier open()-ed the directory to count lines.)
        """
        (tmp_path / "src").mkdir()  # a directory, not a file
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "type": "directory_structure",
             "source_file": "src", "source_lines": [1, 1]}
        ])
        r = VerificationResult()
        validate_source_files(manifest, tmp_path, r)  # must not raise
        assert r.ok is True
        assert len(r.errors) == 0

    def test_file_claim_still_line_checked_after_dir_fix(self, tmp_path):
        """Sanity: the directory-skip fix must not disable line checks for real
        files. A file claim with out-of-range source_lines still errors."""
        (tmp_path / "main.py").write_text("line1\nline2\n", encoding="utf-8")
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_file": "main.py", "source_lines": [1, 99]}
        ])
        r = VerificationResult()
        validate_source_files(manifest, tmp_path, r)
        assert r.ok is False
        assert any("exceeds file length" in e for e in r.errors)

    def test_info_recorded_when_files_checked(self, tmp_path):
        src_file = tmp_path / "src"
        src_file.mkdir()
        (src_file / "main.py").write_text("line1\n", encoding="utf-8")
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_file": "main.py"}
        ])
        r = VerificationResult()
        validate_source_files(manifest, src_file, r)
        assert any("Checked 1 source files" in info for info in r.info)


# ─── find_manifests ─────────────────────────────────────────────


class TestFindManifests:
    def test_finds_brief_manifest(self, tmp_path):
        project = tmp_path / "myproject"
        (project / "docs").mkdir(parents=True)
        (project / "docs" / "sources-manifest.json").write_text("{}", encoding="utf-8")
        results = find_manifests(tmp_path)
        names = [(p, d) for p, d, _ in results]
        assert ("myproject", "brief") in names

    def test_finds_medium_manifest(self, tmp_path):
        project = tmp_path / "myproject"
        (project / "docs" / "medium").mkdir(parents=True)
        (project / "docs" / "medium" / "sources-manifest.json").write_text("{}", encoding="utf-8")
        results = find_manifests(tmp_path)
        names = [(p, d) for p, d, _ in results]
        assert ("myproject", "medium") in names

    def test_finds_deep_manifest(self, tmp_path):
        project = tmp_path / "myproject"
        (project / "docs" / "deep").mkdir(parents=True)
        (project / "docs" / "deep" / "sources-manifest.json").write_text("{}", encoding="utf-8")
        results = find_manifests(tmp_path)
        names = [(p, d) for p, d, _ in results]
        assert ("myproject", "deep") in names

    def test_skips_underscore_prefixed_dirs(self, tmp_path):
        hidden = tmp_path / "_src_project"
        (hidden / "docs").mkdir(parents=True)
        (hidden / "docs" / "sources-manifest.json").write_text("{}", encoding="utf-8")
        results = find_manifests(tmp_path)
        assert len(results) == 0

    def test_returns_empty_for_empty_directory(self, tmp_path):
        results = find_manifests(tmp_path)
        assert results == []

    def test_finds_all_three_depths(self, tmp_path):
        project = tmp_path / "fullproject"
        (project / "docs").mkdir(parents=True)
        (project / "docs" / "sources-manifest.json").write_text("{}", encoding="utf-8")
        (project / "docs" / "medium").mkdir(parents=True)
        (project / "docs" / "medium" / "sources-manifest.json").write_text("{}", encoding="utf-8")
        (project / "docs" / "deep").mkdir(parents=True)
        (project / "docs" / "deep" / "sources-manifest.json").write_text("{}", encoding="utf-8")
        results = find_manifests(tmp_path)
        names = sorted([(p, d) for p, d, _ in results])
        assert names == [("fullproject", "brief"), ("fullproject", "deep"), ("fullproject", "medium")]


# ─── validate_manifest integration ──────────────────────────────


class TestValidateManifest:
    def test_nonexistent_file_is_error(self, tmp_path):
        result = validate_manifest(tmp_path / "no_such_file.json")
        assert result.ok is False
        assert any("not found" in e for e in result.errors)

    def test_invalid_json_is_error(self, tmp_path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{invalid json!!!}", encoding="utf-8")
        result = validate_manifest(bad_json)
        assert result.ok is False
        assert any("Invalid JSON" in e for e in result.errors)

    def test_valid_manifest_passes(self, tmp_path):
        manifest = _make_minimal_manifest()
        path = _write_manifest(tmp_path, manifest)
        result = validate_manifest(path)
        assert result.ok is True

    def test_with_source_dir(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("line1\nline2\n", encoding="utf-8")
        manifest = _make_minimal_manifest(claims=[
            {**_make_full_claim(), "source_file": "main.py"}
        ])
        path = _write_manifest(tmp_path, manifest)
        result = validate_manifest(path, source_dir=src_dir)
        assert result.ok is True

    def test_strict_mode(self, tmp_path):
        manifest = _make_minimal_manifest(claims=[_make_full_claim()])
        path = _write_manifest(tmp_path, manifest)
        result = validate_manifest(path, strict=True)
        assert result.ok is True

    def test_source_project_version_is_allowed(self, tmp_path):
        """Regression: source_project.version must be accepted by the schema
        (Bug 3 — additionalProperties:false rejected it with 'version unexpected')."""
        pytest.importorskip("jsonschema")
        manifest = _make_minimal_manifest()
        manifest["source_project"]["version"] = "1.6.4"
        path = _write_manifest(tmp_path, manifest)
        result = validate_manifest(path)
        assert result.ok is True
        assert not any("version" in e for e in result.errors)


# ─── load_schema ────────────────────────────────────────────────


class TestLoadSchema:
    def test_schema_file_exists_and_loads(self):
        """If the schema file at docs/sources-manifest.schema.json exists, it loads."""
        if not SCHEMA_PATH.exists():
            pytest.skip("Schema file not present in this project")
        schema = load_schema()
        assert isinstance(schema, dict)

    def test_schema_file_missing_returns_none(self, tmp_path, monkeypatch):
        import scripts.verify_sources as vs
        monkeypatch.setattr(vs, "SCHEMA_PATH", tmp_path / "nonexistent.json")
        assert vs.load_schema() is None

    def test_schema_file_invalid_json_returns_none(self, tmp_path, monkeypatch):
        import scripts.verify_sources as vs
        bad = tmp_path / "bad.schema.json"
        bad.write_text("{bad json!!", encoding="utf-8")
        monkeypatch.setattr(vs, "SCHEMA_PATH", bad)
        assert vs.load_schema() is None
