"""
tests/test_update_changelog.py — Validate scripts/update_changelog.py text surgery

Covers: rename of the first `## [Unreleased]` heading + fresh skeleton reinsert,
missing-section atomic failure (exit 1, file untouched), and --date override.
"""

import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent
SCRIPT = ROOT / "scripts" / "update_changelog.py"

FIXTURE = """\
# Changelog

## [Unreleased]

### Added
- new feature A

### Fixed
- bug B

## [0.9.4] - 2026-06-29

### Fixed
- old fix
"""


def _run(args):
    return subprocess.run(
        [sys.executable, str(SCRIPT)] + args,
        capture_output=True,
        text=True,
        timeout=10,
    )


def test_renames_unreleased_and_reinserts_skeleton(tmp_path):
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text(FIXTURE)
    r = _run([str(cl), "0.9.5"])
    assert r.returncode == 0, r.stderr
    today = date.today().isoformat()
    expected = (
        "# Changelog\n"
        "\n"
        "## [Unreleased]\n"
        "\n"
        "### Added\n"
        "\n"
        "### Fixed\n"
        "\n"
        f"## [0.9.5] - {today}\n"
        "\n"
        "### Added\n"
        "- new feature A\n"
        "\n"
        "### Fixed\n"
        "- bug B\n"
        "\n"
        "## [0.9.4] - 2026-06-29\n"
        "\n"
        "### Fixed\n"
        "- old fix\n"
    )
    assert cl.read_text() == expected
    assert cl.read_text().count("## [Unreleased]") == 1


def test_missing_unreleased_section_exits_1_and_leaves_file_untouched(tmp_path):
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text("# Changelog\n\n## [0.9.4] - 2026-06-29\n")
    r = subprocess.run([sys.executable, str(SCRIPT), str(cl), "0.9.5"], capture_output=True, text=True)
    assert r.returncode == 1
    assert "Unreleased" in r.stderr
    assert "## [0.9.4]" in cl.read_text()  # 文件未被改动


def test_date_flag_uses_custom_date(tmp_path):
    cl = tmp_path / "CHANGELOG.md"
    cl.write_text(FIXTURE)
    r = _run([str(cl), "0.9.5", "--date", "2026-12-31"])
    assert r.returncode == 0, r.stderr
    out = cl.read_text()
    assert "## [0.9.5] - 2026-12-31" in out
    assert f"## [0.9.5] - {date.today().isoformat()}" not in out
