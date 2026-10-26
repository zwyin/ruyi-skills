"""Pytest suite for validate_versions.py — driven by the evals fixtures.

Each test runs the checker against one fixture and asserts the outcome matches
the corresponding evals.json expectations. Together with evals/validate.py
(structural regression), this is the quality gate for the skill.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import pytest

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "validate_versions.py"
FIXTURES = SKILL_ROOT / "evals" / "fixtures"

# Mutation primitives the read-only checker must never contain. Assembled via
# concatenation so a security scanner does not flag this test file for naming them.
_FORBIDDEN_PRIMITIVES = [
    "os" + ".system",
    "subprocess" + ".run",
    "subprocess" + ".call",
    "shutil" + ".rmtree",
    ".write(",
]

# Load the checker as a module (it lives under scripts/, not on sys.path).
# Register in sys.modules BEFORE exec_module — Python 3.14's dataclass decorator
# looks up cls.__module__ there during class processing.
_spec = importlib.util.spec_from_file_location("validate_versions", SCRIPT)
assert _spec is not None and _spec.loader is not None, "could not load validate_versions module"
vc = importlib.util.module_from_spec(_spec)
sys.modules["validate_versions"] = vc
_spec.loader.exec_module(vc)


def _run(fixture_name: str):
    return vc.run(FIXTURES / fixture_name)


def _findings(report, status=None, surface_contains=None):
    items = report.findings
    if status:
        items = [f for f in items if f.status == status]
    if surface_contains:
        items = [f for f in items if surface_contains in f.surface]
    return items


# --- fixture 1: Phase 0 banner mismatch ---

def test_fixture1_banner_mismatch_reports_fail():
    report = _run("fixture-1-phase0-banner-mismatch")
    assert report.exit_code == 2
    banner_fails = _findings(report, status="FAIL", surface_contains="banner")
    assert banner_fails, "expected a FAIL on the Phase 0 banner"
    assert any(f.expected == "1.6.5" and f.actual == "1.6.0" for f in banner_fails)
    assert any("SKILL.md" in f.file and f.line > 0 for f in banner_fails)
    flag_fails = _findings(report, status="FAIL", surface_contains="version-flag")
    assert flag_fails, "expected a FAIL on the --version doc string"


# --- fixture 2: all consistent, no noise ---

def test_fixture2_all_consistent_clean():
    report = _run("fixture-2-all-consistent")
    assert report.exit_code == 0
    assert report.fails == 0
    assert report.warns == 0
    assert all(f.status == "PASS" for f in report.findings)


# --- fixture 3: collection CHANGELOG lags marketplace ---

def test_fixture3_changelog_lag_reports_fail():
    report = _run("fixture-3-changelog-lag")
    assert report.exit_code == 2
    cl_fails = _findings(report, status="FAIL", surface_contains="collection CHANGELOG")
    assert cl_fails, "expected a FAIL on the collection CHANGELOG"
    assert cl_fails[0].expected == "0.9.4"
    assert cl_fails[0].actual == "0.9.0"
    assert "insert" in cl_fails[0].hint or "rewrite" in cl_fails[0].hint


# --- fixture 4: dist drift + test literal -> WARN only, no FAIL ---

def test_fixture4_dist_drift_reports_warn_not_fail():
    report = _run("fixture-4-dist-drift")
    assert report.exit_code == 1  # WARN only, not FAIL
    assert report.fails == 0
    dist_warns = _findings(report, status="WARN", surface_contains="dist")
    assert dist_warns, "expected WARN on dist copies"
    assert any("convert.sh" in f.hint for f in dist_warns), "dist hint must suggest convert.sh"
    assert any("frontmatter" in f.surface for f in dist_warns)
    assert any("banner" in f.surface for f in dist_warns)
    test_warns = _findings(report, status="WARN", surface_contains="test version literal")
    assert test_warns, "expected WARN on hardcoded test literal"


# --- fixture 5: multi-skill, all consistent, no false positive ---

def test_fixture5_multi_skill_no_false_positive():
    report = _run("fixture-5-multi-skill-consistent")
    assert report.exit_code == 0
    assert report.fails == 0
    assert report.warns == 0
    skill_md_findings = [f for f in report.findings if "SKILL.md" in f.file]
    assert len({f.file for f in skill_md_findings}) >= 2, "both skills must be checked"


# --- contract: description trigger markers ---

def test_description_carries_three_tier_markers():
    text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    fm = text.split("---", 2)[1]
    for marker in ("ruyi-version-check", "版本检查", "版本一致性检查"):
        assert marker in fm, f"description must mention explicit marker: {marker}"
    assert "不要用于" in fm, "description must carry a negative (do-not-trigger) clause"


@pytest.mark.parametrize("primitive", _FORBIDDEN_PRIMITIVES)
def test_checker_has_no_mutation_primitives(primitive):
    script = SCRIPT.read_text(encoding="utf-8")
    assert primitive not in script, f"checker must stay read-only: found {primitive}"


# --- argument handling ---

def test_missing_skills_dir_returns_error():
    with tempfile.TemporaryDirectory() as tmp:
        code = vc.main(["--root", tmp])
        assert code == 2  # no skills/ -> treated as failure
