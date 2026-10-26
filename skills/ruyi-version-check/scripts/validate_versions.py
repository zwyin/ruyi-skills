#!/usr/bin/env python3
"""Deterministic version-consistency checker for a ruyi-skills collection.

Reads the canonical version from each skill's SKILL.md frontmatter and verifies
every version surface — manifests, Phase 0 banner, README badges, CHANGELOG,
dist platform copies, and test-fixture literals — agrees with it. Also checks
the collection-layer version (marketplace.json vs CHANGELOG).

Pure read-only: produces a report and exits non-zero on mismatch. Never mutates
files. Designed to run before release, on suspected version drift, and in CI.

Usage:
    validate_versions.py [--root <collection-root>] [--skill <name>] [--format text|json] [--strict]

Exit codes: 2 = one or more failures. Default mode: 0 = consistent or warnings only
(WARNs never block CI). --strict (pre-release checks): 1 = warnings only, 0 = clean.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

SEMVER = r"\d+\.\d+\.\d+"
SEMVER_RE = re.compile(SEMVER)

# Patterns that declare "the current version" inside SKILL.md body. Scoped
# (not a bare scan of every X.Y.Z) so historical / third-party versions do not
# produce noise. Triple-quoted raw strings so the ["'] char class is unambiguous.
SKILL_BODY_PATTERNS = [
    ("Phase 0 banner", re.compile(r""">\s*\*\*Version\s+(""" + SEMVER + r""")\*\*""")),
    ("version-flag doc", re.compile(r"""--version\b[^\n]*?\bv(""" + SEMVER + r""")\b""")),
    ("startup version print", re.compile(r"""Project Walkthrough\s+v(""" + SEMVER + r""")\b""")),
]

_QUOTED = r"""["']?"""
FM_VERSION_RE = re.compile(
    r"""^version:\s*""" + _QUOTED + r"""(""" + SEMVER + r""")""" + _QUOTED + r"""\s*$""",
    re.MULTILINE,
)
BADGE_RE = re.compile(r"""version-(""" + SEMVER + r""")""")
CHANGELOG_HEAD_RE = re.compile(r"""^##\s*\[(""" + SEMVER + r""")\]""", re.MULTILINE)
TEST_LITERAL_RE = re.compile(r"""["']v?(""" + SEMVER + r""")["']""")
BANNER_RE = re.compile(r""">\s*\*\*Version\s+(""" + SEMVER + r""")\*\*""")


@dataclass
class Finding:
    status: str  # "PASS" | "WARN" | "FAIL"
    surface: str
    file: str  # repo-relative path
    line: int  # 1-based; 0 if not applicable
    expected: str
    actual: str
    hint: str = ""


@dataclass
class Report:
    root: str
    collection_version: str = ""
    findings: list = field(default_factory=list)

    @property
    def fails(self):
        return sum(1 for f in self.findings if f.status == "FAIL")

    @property
    def warns(self):
        return sum(1 for f in self.findings if f.status == "WARN")

    @property
    def passes(self):
        return sum(1 for f in self.findings if f.status == "PASS")

    def exit_code(self, strict: bool = False) -> int:
        """Single source of truth for the exit code (main/render_text/render_json all call this).

        FAIL always exits 2. WARN exits 1 only under --strict (pre-release checks);
        in default mode WARNs are reported but never affect the exit code.
        """
        if self.fails:
            return 2
        if strict and self.warns:
            return 1
        return 0


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def line_of(text: str, substring: str) -> int:
    idx = text.find(substring)
    return text.count("\n", 0, idx) + 1 if idx >= 0 else 0


def read_frontmatter_version(skill_md: Path):
    text = read_text(skill_md)
    if not text:
        return None
    parts = text.split("---", 2)
    block = parts[1] if len(parts) >= 3 else text
    m = FM_VERSION_RE.search(block)
    return m.group(1) if m else None


def json_version(path: Path):
    if not path.is_file():
        return None
    try:
        data = json.loads(read_text(path))
    except json.JSONDecodeError:
        return None
    v = data.get("version")
    return v if isinstance(v, str) and SEMVER_RE.fullmatch(v) else None


def changelog_latest(path: Path):
    if not path.is_file():
        return None
    m = CHANGELOG_HEAD_RE.search(read_text(path))
    return m.group(1) if m else None


def all_badge_versions(path: Path) -> list:
    if not path.is_file():
        return []
    return BADGE_RE.findall(read_text(path))


def first_badge_version(path: Path):
    badges = all_badge_versions(path)
    return badges[0] if badges else None


def discover_skills(root: Path):
    """Return [(skill_name, canonical_skill_md, skill_top_dir)] per skill.

    Canonical SKILL.md lives at `skills/<name>/skills/<name>/SKILL.md` (the
    symlink target). Manifests / CHANGELOG / README / tests live one level up
    at the skill top dir `skills/<name>/`.
    """
    skills = []
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return skills
    for skill_md in sorted(skills_root.glob("*/skills/*/SKILL.md")):
        name = skill_md.parts[-2]  # .../skills/<name>/SKILL.md -> <name>
        skill_top = skill_md.parents[2]  # skills/<name>/
        skills.append((name, skill_md, skill_top))
    return skills


def _record(report, status, surface, file, root, canonical, actual, hint=""):
    rel = str(file.relative_to(root))
    if actual is None:
        report.findings.append(Finding(status, surface, rel, 0, canonical, "missing",
                                       hint or f"add version {canonical}"))
    elif actual != canonical:
        line = line_of(read_text(file), actual)
        report.findings.append(Finding(status, surface, rel, line, canonical, actual, hint))
    else:
        report.findings.append(Finding("PASS", surface, rel, 0, canonical, actual))


def _record_badge_membership(report, surface, readme_path, root, canonical):
    """Collection README has multiple skills' badges; verify canonical is present."""
    badges = all_badge_versions(readme_path)
    rel = str(readme_path.relative_to(root)) if readme_path.is_absolute() or len(readme_path.parts) > 1 else str(readme_path)
    if not badges:
        report.findings.append(Finding("FAIL", surface, rel, 0, canonical, "none",
                                       f"no version badge in {rel}; add version-{canonical}"))
    elif canonical in badges:
        report.findings.append(Finding("PASS", surface, rel, 0, canonical, canonical))
    else:
        report.findings.append(Finding("FAIL", surface, rel, 0, canonical, ",".join(badges),
                                       f"canonical {canonical} has no badge in {rel}; add version-{canonical}"))


def _check_dist(report, root, name, canonical):
    dist_root = root / "dist"
    if not dist_root.is_dir():
        return
    for platform_dir in dist_root.glob("*"):
        if not platform_dir.is_dir():
            continue
        for md_file in platform_dir.rglob("*"):
            if not md_file.is_file() or md_file.suffix not in (".md", ".mdc"):
                continue
            # skill name lives in the path (.opencode/skills/<name>/), not the filename
            if name not in str(md_file.relative_to(platform_dir)):
                continue
            text = md_file.read_text(encoding="utf-8", errors="ignore")
            fm = FM_VERSION_RE.search(text)
            if fm and fm.group(1) != canonical:
                line = text.count("\n", 0, fm.start()) + 1
                report.findings.append(Finding("WARN", f"dist/{platform_dir.name} frontmatter",
                                               str(md_file.relative_to(root)), line, canonical, fm.group(1),
                                               "dist drift; rerun `bash scripts/convert.sh --all`"))
            bm = BANNER_RE.search(text)
            if bm and bm.group(1) != canonical:
                line = text.count("\n", 0, bm.start()) + 1
                report.findings.append(Finding("WARN", f"dist/{platform_dir.name} banner",
                                               str(md_file.relative_to(root)), line, canonical, bm.group(1),
                                               "dist drift; rerun `bash scripts/convert.sh --all`"))


def _check_test_literals(report, root, skill_top, name, canonical):
    tests_dir = skill_top / "tests"
    if not tests_dir.is_dir():
        return
    name_lower = name.lower()
    for py_file in tests_dir.glob("*.py"):
        for line_no, line in enumerate(read_text(py_file).splitlines(), 1):
            if name_lower not in line.lower() and "version" not in line.lower():
                continue
            for m in TEST_LITERAL_RE.finditer(line):
                if m.group(1) != canonical:
                    report.findings.append(Finding("WARN", "test version literal",
                                                   str(py_file.relative_to(root)), line_no, canonical, m.group(1),
                                                   "hardcoded version in test; if this is fixture data (fake frontmatter), ignore; if it asserts the skill version, update"))


def check_skill(report, root, name, skill_md, skill_top):
    canonical = read_frontmatter_version(skill_md)
    if not canonical:
        report.findings.append(Finding("FAIL", "frontmatter version", str(skill_md.relative_to(root)), 3,
                                       "", "missing", 'add `version: "X.Y.Z"` to SKILL.md frontmatter'))
        return

    # 1-2: manifests (at skill top, not nested canonical dir)
    _record(report, "FAIL", "plugin.json version",
            skill_top / ".claude-plugin" / "plugin.json", root, canonical,
            json_version(skill_top / ".claude-plugin" / "plugin.json"))
    _record(report, "FAIL", "marketplace.json version",
            skill_top / ".claude-plugin" / "marketplace.json", root, canonical,
            json_version(skill_top / ".claude-plugin" / "marketplace.json"))
    # 3: skill CHANGELOG
    _record(report, "FAIL", "skill CHANGELOG latest", skill_top / "CHANGELOG.md", root, canonical,
            changelog_latest(skill_top / "CHANGELOG.md"),
            hint="CHANGELOG title out of sync; update `## [X.Y.Z] - YYYY-MM-DD`")
    # 4: skill own README badge
    _record(report, "FAIL", "skill README badge", skill_top / "README.md", root, canonical,
            first_badge_version(skill_top / "README.md"))
    # 5: collection README badges (zh always; en optional) — membership check
    for readme in ("README.md", "README.en.md"):
        readme_path = root / readme
        if not readme_path.is_file():
            continue  # optional file (e.g. no English README) — skip silently
        _record_badge_membership(report, f"collection {readme} badge", readme_path, root, canonical)
    # 6: SKILL.md body version declarations (Phase 0 banner, --version doc)
    rel_skill_md = str(skill_md.relative_to(root))
    body = read_text(skill_md)
    for label, pattern in SKILL_BODY_PATTERNS:
        for m in pattern.finditer(body):
            actual = m.group(1)
            line = body.count("\n", 0, m.start()) + 1
            if actual != canonical:
                report.findings.append(Finding("FAIL", label, rel_skill_md, line, canonical, actual,
                                               "release.sh sed pattern likely misses this format; sync manually"))
            else:
                report.findings.append(Finding("PASS", label, rel_skill_md, line, canonical, actual))
    # 7: dist platform copies (WARN — rerun convert.sh, do not hand-edit)
    _check_dist(report, root, name, canonical)
    # 8: hardcoded version literals in tests (WARN)
    _check_test_literals(report, root, skill_top, name, canonical)


def check_collection(report, root):
    marketplace = root / ".claude-plugin" / "marketplace.json"
    coll = json_version(marketplace)
    if not coll:
        report.findings.append(Finding("FAIL", "collection version", str(marketplace.relative_to(root)), 0,
                                       "", "missing", 'add "version": "X.Y.Z" to collection marketplace.json'))
        return
    report.collection_version = coll
    report.findings.append(Finding("PASS", "collection version", str(marketplace.relative_to(root)), 0, "", coll))
    cl_path = root / "CHANGELOG.md"
    cl = changelog_latest(cl_path)
    rel = str(cl_path.relative_to(root))
    if cl is None:
        report.findings.append(Finding("FAIL", "collection CHANGELOG latest", rel, 0, coll, "missing",
                                       "release.sh only rewrites existing entries; insert the missing version block"))
    elif cl != coll:
        line = line_of(read_text(cl_path), cl)
        report.findings.append(Finding("FAIL", "collection CHANGELOG latest", rel, line, coll, cl,
                                       "release.sh only rewrites existing entries; insert the missing version block"))
    else:
        report.findings.append(Finding("PASS", "collection CHANGELOG latest", rel, 0, coll, cl))


def run(root, skill_filter=None):
    report = Report(root=str(root))
    check_collection(report, root)
    for name, skill_md, skill_top in discover_skills(root):
        if skill_filter and name != skill_filter:
            continue
        check_skill(report, root, name, skill_md, skill_top)
    return report


def render_text(report, strict: bool = False):
    out = ["=== ruyi-version-check ===", f"root: {report.root}"]
    if report.collection_version:
        out.append(f"collection version: {report.collection_version}")
    out.append("")
    for f in report.findings:
        if f.status == "PASS":
            continue
        loc = f"{f.file}:{f.line}" if f.line else f.file
        out.append(f"[{f.status}] {loc}")
        expected_disp = f.expected or "<present>"
        out.append(f"      {f.surface}: expected {expected_disp}, found {f.actual}")
        if f.hint:
            out.append(f"      -> {f.hint}")
    out.append("")
    out.append(f"Summary: {report.fails} FAIL, {report.warns} WARN, {report.passes} PASS "
               f"(exit {report.exit_code(strict)})")
    return "\n".join(out)


def render_json(report, strict: bool = False):
    return json.dumps({
        "root": report.root,
        "collection_version": report.collection_version,
        "summary": {"fail": report.fails, "warn": report.warns, "pass": report.passes},
        "exit_code": report.exit_code(strict),
        "findings": [asdict(f) for f in report.findings if f.status != "PASS"],
    }, indent=2, ensure_ascii=False)


def main(argv=None):
    parser = argparse.ArgumentParser(description="ruyi-skills version consistency checker")
    parser.add_argument("--root", default=".", help="collection root (default: cwd)")
    parser.add_argument("--skill", default=None, help="check a single skill by name")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true",
                        help="warnings-only exits 1 (pre-release strict mode); "
                             "default mode never lets WARNs affect the exit code")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    if not (root / "skills").is_dir():
        print(f"[ERR] no skills/ directory under {root}", file=sys.stderr)
        return 2

    report = run(root, args.skill)
    print(render_json(report, args.strict) if args.format == "json"
          else render_text(report, args.strict))
    return report.exit_code(args.strict)


if __name__ == "__main__":
    sys.exit(main())
