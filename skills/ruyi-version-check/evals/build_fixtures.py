#!/usr/bin/env python3
"""Generate minimal static fixtures for the ruyi-version-check eval suite.

Each fixture is a tiny self-contained "skill collection" that exercises one
specific branch of validate_versions.py. Run this once to (re)create the
static fixture trees under evals/fixtures/. The fixtures themselves are
committed (reviewable); this script is kept so they can be rebuilt deterministically.

Layout per fixture (mirrors a real ruyi-skills collection in miniature):
    <fixture>/
      .claude-plugin/marketplace.json     # collection version
      CHANGELOG.md                         # collection changelog latest
      README.md                            # collection badges
      skills/demo-skill/
        README.md                          # skill badge
        CHANGELOG.md                       # skill changelog latest
        .claude-plugin/{plugin,marketplace}.json
        skills/demo-skill/SKILL.md         # canonical: frontmatter + Phase 0 banner
"""

from __future__ import annotations

import json
from pathlib import Path

FIXTURES_ROOT = Path(__file__).parent / "fixtures"
TODAY = "2026-07-27"


def skill_md(canonical: str, banner: str | None = None) -> str:
    banner_line = banner if banner is not None else canonical
    return (
        "---\n"
        f'name: demo-skill\n'
        f'version: "{canonical}"\n'
        f'description: Demo skill for version-check fixtures.\n'
        "argument-hint: \"[--version]\"\n"
        "---\n\n"
        "# Demo Skill\n\n"
        f"> **Version {banner_line}** — Phase 0 banner.\n\n"
        f"Run `demo-skill --version` to print `demo-skill v{banner_line}` and exit.\n"
    )


def plugin_json(version: str) -> str:
    return json.dumps({
        "name": "demo-skill",
        "version": version,
        "description": "Demo skill",
        "skills": "./skills/",
    }, indent=2) + "\n"


def marketplace_json_skill(version: str) -> str:
    return json.dumps({
        "name": "demo-skill",
        "version": version,
        "owner": {"name": "tester"},
        "plugins": [{"name": "demo-skill", "source": "./", "category": "tooling"}],
    }, indent=2) + "\n"


def marketplace_json_collection(version: str) -> str:
    return json.dumps({
        "name": "demo-collection",
        "version": version,
        "owner": {"name": "tester"},
        "plugins": [{"name": "demo-collection", "source": "./",
                     "skills": ["./skills/demo-skill/skills/demo-skill"]}],
    }, indent=2) + "\n"


def changelog(version: str) -> str:
    return (
        "# Changelog\n\n"
        f"## [{version}] - {TODAY}\n\n"
        "### Added\n- test fixture entry\n"
    )


def readme(badge_versions: list[str]) -> str:
    lines = ["# Demo Collection\n"]
    for v in badge_versions:
        lines.append(f'[![version](https://img.shields.io/badge/version-{v}-blue)](./CHANGELOG.md)')
    return "\n".join(lines) + "\n"


def write_base(root: Path, skill_canonical: str, collection_version: str,
               banner: str | None = None, skill_changelog: str | None = None,
               collection_changelog: str | None = None,
               skill_badge: str | None = None, collection_badges: list[str] | None = None) -> None:
    """Write a fully-consistent base collection, then let callers override specifics."""
    sc = skill_canonical
    (root / "skills" / "demo-skill" / "skills" / "demo-skill").mkdir(parents=True, exist_ok=True)
    (root / "skills" / "demo-skill" / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (root / ".claude-plugin").mkdir(parents=True, exist_ok=True)

    (root / "skills" / "demo-skill" / "skills" / "demo-skill" / "SKILL.md").write_text(skill_md(sc, banner), encoding="utf-8")
    (root / "skills" / "demo-skill" / ".claude-plugin" / "plugin.json").write_text(plugin_json(sc), encoding="utf-8")
    (root / "skills" / "demo-skill" / ".claude-plugin" / "marketplace.json").write_text(marketplace_json_skill(sc), encoding="utf-8")
    (root / "skills" / "demo-skill" / "CHANGELOG.md").write_text(changelog(skill_changelog or sc), encoding="utf-8")
    (root / "skills" / "demo-skill" / "README.md").write_text(readme([skill_badge or sc]), encoding="utf-8")
    (root / ".claude-plugin" / "marketplace.json").write_text(marketplace_json_collection(collection_version), encoding="utf-8")
    (root / "CHANGELOG.md").write_text(changelog(collection_changelog or collection_version), encoding="utf-8")
    (root / "README.md").write_text(readme(collection_badges or [sc]), encoding="utf-8")


def write_dist(root: Path, dist_version: str, dist_banner: str) -> None:
    """Add a drifting dist/opencode copy (used by fixture-4)."""
    dist_md = root / "dist" / "opencode" / ".opencode" / "skills" / "demo-skill"
    dist_md.mkdir(parents=True, exist_ok=True)
    (dist_md / "SKILL.md").write_text(skill_md(dist_version, dist_banner), encoding="utf-8")


def write_test_literal(root: Path, literal_version: str) -> None:
    """Add a test file with a hardcoded version literal (used by fixture variants)."""
    tests = root / "skills" / "demo-skill" / "tests"
    tests.mkdir(parents=True, exist_ok=True)
    (tests / "test_demo.py").write_text(
        f'def test_version():\n    assert demo_version == "{literal_version}"\n', encoding="utf-8"
    )


def fixture_1_banner_mismatch() -> None:
    """frontmatter=1.6.5 but Phase 0 banner=1.6.0 -> FAIL on banner."""
    root = FIXTURES_ROOT / "fixture-1-phase0-banner-mismatch"
    write_base(root, skill_canonical="1.6.5", collection_version="0.9.4", banner="1.6.0")


def fixture_2_all_consistent() -> None:
    """Everything agrees -> 0 FAIL, 0 WARN."""
    root = FIXTURES_ROOT / "fixture-2-all-consistent"
    write_base(root, skill_canonical="1.6.5", collection_version="0.9.4")


def fixture_3_changelog_lag() -> None:
    """collection marketplace=0.9.4 but CHANGELOG=0.9.0 -> FAIL collection CHANGELOG."""
    root = FIXTURES_ROOT / "fixture-3-changelog-lag"
    write_base(root, skill_canonical="1.6.5", collection_version="0.9.4", collection_changelog="0.9.0")


def fixture_4_dist_drift() -> None:
    """canonical=1.6.5, dist/opencode copy at 1.6.4/1.6.0 -> WARN dist drift."""
    root = FIXTURES_ROOT / "fixture-4-dist-drift"
    write_base(root, skill_canonical="1.6.5", collection_version="0.9.4")
    write_dist(root, dist_version="1.6.4", dist_banner="1.6.0")
    write_test_literal(root, literal_version="1.6.4")  # also exercise WARN test-literal path


def fixture_5_multi_skill_consistent() -> None:
    """Two skills, both fully consistent -> 0 FAIL, 0 WARN."""
    root = FIXTURES_ROOT / "fixture-5-multi-skill-consistent"
    write_base(root, skill_canonical="1.6.5", collection_version="0.9.4",
               collection_badges=["1.6.5", "0.7.0"])
    # add a second consistent skill
    second = root / "skills" / "second-skill"
    (second / "skills" / "second-skill").mkdir(parents=True, exist_ok=True)
    (second / ".claude-plugin").mkdir(parents=True, exist_ok=True)
    (second / "skills" / "second-skill" / "SKILL.md").write_text(
        skill_md("0.7.0").replace("demo-skill", "second-skill"), encoding="utf-8")
    (second / ".claude-plugin" / "plugin.json").write_text(
        plugin_json("0.7.0").replace("demo-skill", "second-skill"), encoding="utf-8")
    (second / ".claude-plugin" / "marketplace.json").write_text(
        marketplace_json_skill("0.7.0").replace("demo-skill", "second-skill"), encoding="utf-8")
    (second / "CHANGELOG.md").write_text(changelog("0.7.0"), encoding="utf-8")
    (second / "README.md").write_text(readme(["0.7.0"]), encoding="utf-8")


def main() -> None:
    if FIXTURES_ROOT.exists():
        import shutil
        shutil.rmtree(FIXTURES_ROOT)
    FIXTURES_ROOT.mkdir(parents=True)
    fixture_1_banner_mismatch()
    fixture_2_all_consistent()
    fixture_3_changelog_lag()
    fixture_4_dist_drift()
    fixture_5_multi_skill_consistent()
    count = sum(1 for _ in FIXTURES_ROOT.rglob("*") if _.is_file())
    print(f"[OK] built {len(list(FIXTURES_ROOT.iterdir()))} fixtures, {count} files under {FIXTURES_ROOT}")


if __name__ == "__main__":
    main()
