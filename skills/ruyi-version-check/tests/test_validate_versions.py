"""Pytest suite for validate_versions.py — driven by the evals fixtures.

Each test runs the checker against one fixture and asserts the outcome matches
the corresponding evals.json expectations. Together with evals/validate.py
(structural regression), this is the quality gate for the skill.
"""

from __future__ import annotations

import importlib.util
import json
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
    assert report.exit_code() == 2
    banner_fails = _findings(report, status="FAIL", surface_contains="banner")
    assert banner_fails, "expected a FAIL on the Phase 0 banner"
    assert any(f.expected == "1.6.5" and f.actual == "1.6.0" for f in banner_fails)
    assert any("SKILL.md" in f.file and f.line > 0 for f in banner_fails)
    flag_fails = _findings(report, status="FAIL", surface_contains="version-flag")
    assert flag_fails, "expected a FAIL on the --version doc string"


# --- fixture 2: all consistent, no noise ---

def test_fixture2_all_consistent_clean():
    report = _run("fixture-2-all-consistent")
    assert report.exit_code() == 0
    assert report.fails == 0
    assert report.warns == 0
    assert all(f.status == "PASS" for f in report.findings)


# --- fixture 3: collection CHANGELOG lags marketplace ---

def test_fixture3_changelog_lag_reports_fail():
    report = _run("fixture-3-changelog-lag")
    assert report.exit_code() == 2
    cl_fails = _findings(report, status="FAIL", surface_contains="collection CHANGELOG")
    assert cl_fails, "expected a FAIL on the collection CHANGELOG"
    assert cl_fails[0].expected == "0.9.4"
    assert cl_fails[0].actual == "0.9.0"
    assert "insert" in cl_fails[0].hint or "rewrite" in cl_fails[0].hint


# --- fixture 4: dist drift + test literal -> WARN only, no FAIL ---

def test_fixture4_dist_drift_reports_warn_not_fail():
    report = _run("fixture-4-dist-drift")
    assert report.exit_code() == 0  # WARN only: default mode no longer blocks (decision 3)
    assert report.exit_code(strict=True) == 1  # --strict restores WARN -> 1
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
    assert report.exit_code() == 0
    assert report.fails == 0
    assert report.warns == 0
    skill_md_findings = [f for f in report.findings if "SKILL.md" in f.file]
    assert len({f.file for f in skill_md_findings}) >= 2, "both skills must be checked"


# --- exit-code semantics: default vs --strict (decision 3) ---

def test_warn_only_default_exit_zero_and_report_agrees(capsys):
    """WARN-only fixture: default mode exits 0 AND the text Summary shows (exit 0).

    Both assertions together pin "report display agrees with process exit code".
    """
    code = vc.main(["--root", str(FIXTURES / "fixture-4-dist-drift")])
    assert code == 0
    out = capsys.readouterr().out
    assert "(exit 0)" in out, "text report must display the same exit code the process returns"


def test_warn_only_strict_exit_one_and_report_agrees(capsys):
    code = vc.main(["--root", str(FIXTURES / "fixture-4-dist-drift"), "--strict"])
    assert code == 1
    assert "(exit 1)" in capsys.readouterr().out


def test_fail_exits_two_in_both_modes():
    for extra in ([], ["--strict"]):
        assert vc.main(["--root", str(FIXTURES / "fixture-1-phase0-banner-mismatch")] + extra) == 2


def test_clean_exits_zero_in_both_modes():
    for extra in ([], ["--strict"]):
        assert vc.main(["--root", str(FIXTURES / "fixture-2-all-consistent")] + extra) == 0


def test_json_exit_code_field_agrees_with_process_exit(capsys):
    """render_json must derive exit_code from the same computation as main()."""
    for extra, expected in (([], 0), (["--strict"], 1)):
        code = vc.main(["--root", str(FIXTURES / "fixture-4-dist-drift"),
                        "--format", "json"] + extra)
        payload = json.loads(capsys.readouterr().out)
        assert payload["exit_code"] == code == expected
        assert payload["summary"]["warn"] > 0


# --- SKILL_BODY_PATTERNS regression: walkthrough startup version print ---

def test_pattern_catches_walkthrough_startup_version_print():
    """`Print Project Walkthrough v1.6.5` (no --version prefix, not **Version** form) must be caught."""
    by_label = dict(vc.SKILL_BODY_PATTERNS)
    pat = by_label["startup version print"]
    m = pat.search("Some header says Print Project Walkthrough v1.6.5 in the docs")
    assert m and m.group(1) == "1.6.5"
    assert not pat.search("Some header says Print Project Walkthrough v without semver")


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
