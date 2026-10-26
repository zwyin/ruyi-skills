"""
tests/test_release_sh.py — Validate scripts/release.sh argument handling and source wiring

Only tests validation guards (no side effects like commit/tag/push).

取舍说明（tradeoff）：本文件不构造临时 git 仓库去跑一次真实发版——
release.sh 会 commit/tag/push，任何"真跑"都有不可逆副作用。
因此对 Unreleased 流程/代理/add 列表的验证采用两条无副作用路径：
  1. 对 release.sh 源码做 grep 式断言（TestReleaseShSource）；
  2. "CHANGELOG 缺 ## [Unreleased] 段时组合行为如何失败"已由
     tests/test_update_changelog.py 覆盖（exit 1 + 文件不被改动）。
"""

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "release.sh"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"


def _run(args, **kwargs):
    return subprocess.run(
        ["bash", str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(ROOT),
        **kwargs,
    )


class TestReleaseShArgs:
    def test_invalid_bump_type_rejected(self):
        for bad in ["hotfix", "1.0", "pre"]:
            r = _run([bad])
            assert r.returncode != 0, f"Should reject bump type: '{bad}'"

    def test_script_is_executable(self):
        assert os.access(str(SCRIPT), os.X_OK), "release.sh should be executable"

    def test_reads_version_from_marketplace(self):
        data = json.loads(MARKETPLACE.read_text())
        version = data["version"]
        parts = version.split(".")
        assert len(parts) == 3, f"Version should be semver, got: {version}"
        assert all(p.isdigit() for p in parts), f"Non-numeric version parts: {version}"


def _src():
    return SCRIPT.read_text()


def _first_line_index(lines, *substrings):
    """Index of the first line containing ALL substrings (fail loudly if absent)."""
    for i, line in enumerate(lines):
        if all(s in line for s in substrings):
            return i
    raise AssertionError(
        f"No line containing all of {substrings!r} found in release.sh"
    )


class TestReleaseShSource:
    """Source-level assertions for the Unreleased release flow (see module docstring)."""

    def test_unreleased_guard_present_with_exit_1(self):
        src = _src()
        assert "grep -q '^## \\[Unreleased\\]' \"$CHANGELOG\"" in src, (
            "release.sh must guard on the ## [Unreleased] heading before releasing"
        )
        assert "先写 Unreleased 再发版" in src, "guard must explain the remediation"
        assert "exit 1" in src

    def test_guard_precedes_marketplace_edit(self):
        # THE critical ordering property: a missing Unreleased section must exit
        # while marketplace.json is still untouched, so the guard must sit before
        # the marketplace.json version rewrite.
        lines = _src().splitlines()
        guard_idx = _first_line_index(lines, "grep -q '^## \\[Unreleased\\]'")
        marketplace_idx = _first_line_index(lines, "perl", "$MARKETPLACE")
        assert guard_idx < marketplace_idx, (
            f"Unreleased guard (line {guard_idx + 1}) must run BEFORE the "
            f"marketplace.json version edit (line {marketplace_idx + 1})"
        )

    def test_guard_after_version_calculation(self):
        lines = _src().splitlines()
        guard_idx = _first_line_index(lines, "grep -q '^## \\[Unreleased\\]'")
        next_idx = _first_line_index(lines, "NEXT=")
        assert guard_idx > next_idx, "guard belongs after $NEXT is calculated"

    def test_changelog_updated_via_update_changelog_py(self):
        src = _src()
        assert 'python3 scripts/update_changelog.py "$CHANGELOG" "$NEXT"' in src, (
            "CHANGELOG rotation must go through scripts/update_changelog.py"
        )
        # The old perl rename (s/## \[CURRENT\]/## [NEXT] - date/) must be gone.
        assert not any(
            "perl" in line and "CHANGELOG" in line for line in src.splitlines()
        ), "old perl CHANGELOG rename must be removed"

    def test_push_bypasses_proxy(self):
        src = _src()
        assert 'git -c http.proxy="" -c https.proxy="" push "$MAIN_REMOTE" main --tags' in src, (
            "push must bypass the local HTTPS-intercepting proxy explicitly"
        )

    def test_git_add_is_explicit_list(self):
        src = _src()
        assert 'git add "$MARKETPLACE" "$CHANGELOG" README.md README.en.md' in src, (
            "git add must stage an explicit file list, not the whole tree"
        )
        assert "git add -A" not in src, "git add -A sweeps unrelated files into releases"
