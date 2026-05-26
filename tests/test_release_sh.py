"""
tests/test_release_sh.py — Validate scripts/release.sh argument handling

Only tests validation guards (no side effects like commit/tag/push).
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
