"""Tests for scripts/release.sh — validation logic only (no actual release)."""

import os
import subprocess

SCRIPT = "scripts/release.sh"


def _run(args, **kwargs):
    return subprocess.run(
        ["bash", SCRIPT] + args,
        capture_output=True,
        text=True,
        timeout=10,
        **kwargs,
    )


class TestReleaseShValidation:
    """Test argument validation guards (no side effects)."""

    def test_no_args_exits_with_error(self):
        r = _run([])
        assert r.returncode != 0
        assert "Usage" in r.stderr or "Usage" in r.stdout

    def test_invalid_version_rejected(self):
        for bad in ["1.0", "abc", "1.0.0.0", "v1.0.0", ""]:
            r = _run([bad])
            assert r.returncode != 0, f"Should reject: {bad}"
            assert "semver" in r.stderr.lower() or "version" in r.stderr.lower()

    def test_valid_version_passes_dry_run(self):
        r = _run(["1.3.0", "--dry-run"])
        assert r.returncode == 0
        assert "Dry run" in r.stdout

    def test_dry_run_exits_before_branch_check(self):
        # Works even on non-develop branches (CI uses detached HEAD)
        r = _run(["99.99.99", "--dry-run"])
        assert r.returncode == 0
        assert "branch" not in r.stderr.lower()

    def test_script_is_executable(self):
        assert os.access(SCRIPT, os.X_OK), "release.sh should be executable"
