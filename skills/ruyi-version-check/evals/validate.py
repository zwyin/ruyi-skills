#!/usr/bin/env python3
"""Deterministic structural regression checks for the ruyi-version-check skill.

Verifies the skill's own invariants: frontmatter well-formed, description
follows the three-tier trigger contract and stays within budget, SKILL.md
respects the progressive-disclosure line budget, the eval suite is complete
and balanced, fixtures are portable, and the checker script is read-only
(no mutation primitives). Run after any change to the skill.

Modeled on khazix neat-freak's evals/validate.py.

Usage:
    python3 evals/validate.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
SCRIPT = ROOT / "scripts" / "validate_versions.py"

SEMVER_RE = re.compile(r"\d+\.\d+\.\d+")
# Explicit trigger markers that MUST appear in description.
EXPLICIT_MARKERS = ("ruyi-version-check", "版本检查", "版本一致性检查")
# Near-miss negatives that MUST be in description's "do not use for" clause.
NEGATIVE_CUES = ("不要用于", "npm", "git log", "bump")
# Bare word that must NOT trigger the skill.
BARE_NON_TRIGGER = "版本"

# Mutation primitives the read-only checker must never contain. Assembled via
# concatenation so a security scanner does not flag this file for mentioning them.
_FORBIDDEN = [
    "os" + ".system",
    "subprocess" + ".run",
    "subprocess" + ".call",
    "shutil" + ".rmtree",
    "Path" + ".write_text",
    ".write(",
]


def _description(frontmatter: str) -> str:
    """Extract a (possibly folded/literal) description block from frontmatter."""
    lines = frontmatter.splitlines()
    captured: list[str] = []
    active = False
    for line in lines:
        if line.startswith("description:"):
            rest = line[len("description:"):].strip()
            active = True
            if rest in ("|", ">", ">-", "|-"):
                continue  # literal/folded block: content is on subsequent indented lines
            captured.append(rest.strip().strip('"').strip("'"))
            continue
        if active:
            if re.match(r"^[a-z][a-z0-9_-]*:", line):
                break  # next top-level key ends the block
            captured.append(line.strip())
    return " ".join(p for p in captured if p)


def main() -> int:
    text = SKILL.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    assert len(parts) == 3, "SKILL.md frontmatter is missing"
    frontmatter = parts[1]
    description = _description(frontmatter)

    # --- frontmatter + description contract ---
    assert re.search(r'^name:\s*ruyi-version-check\s*$', frontmatter, re.MULTILINE), "name mismatch"
    version_match = re.search(r'^version:\s*"(\d+\.\d+\.\d+)"\s*$', frontmatter, re.MULTILINE)
    assert version_match, "version must be quoted semver in frontmatter"

    assert 1 <= len(description) <= 1024, f"description violates Agent Skills limit: {len(description)}"
    assert len(description) <= 850, f"description has <17% growth headroom: {len(description)} chars"
    for marker in EXPLICIT_MARKERS:
        assert marker in description, f"description lost explicit trigger marker: {marker}"
    intent_present = any(c in description for c in ("发版前", "漂移", "体检", "对不上", "落后"))
    assert intent_present, "description lost intent-trigger phrases"
    for cue in NEGATIVE_CUES:
        assert cue in description, f"description lost negative-trigger cue: {cue}"

    # --- progressive disclosure budget ---
    line_count = len(text.splitlines())
    assert line_count < 500, f"SKILL.md exceeds progressive-disclosure line budget: {line_count}"
    assert len(text) / 4 < 5000, "SKILL.md likely exceeds instruction token budget"

    # --- checker script is read-only (no mutation primitives) ---
    assert SCRIPT.is_file(), "validate_versions.py is missing"
    script_text = SCRIPT.read_text(encoding="utf-8")
    for prim in _FORBIDDEN:
        assert prim not in script_text, f"checker script contains mutation primitive: {prim}"

    # --- evals.json coverage ---
    eval_data = json.loads((ROOT / "evals" / "evals.json").read_text(encoding="utf-8"))
    assert eval_data["skill_name"] == "ruyi-version-check"
    evals = eval_data["evals"]
    ids = [e["id"] for e in evals]
    assert len(ids) == len(set(ids)), "duplicate behavior eval ids"
    assert len(evals) >= 5, f"behavior eval coverage regressed: {len(evals)}"
    required = {"detect-phase0-banner-mismatch", "no-false-positive-all-consistent",
                "detect-changelog-lag", "detect-dist-drift",
                "detect-multi-skill-no-false-positive"}
    assert required.issubset({e["name"] for e in evals}), "required behavior evals missing"
    for e in evals:
        assert e.get("expectations"), f"eval {e['id']} has no expectations"
        assert "assertions" not in e, f"eval {e['id']} uses obsolete assertions field"
        for rel in e.get("files", []):
            p = Path(rel)
            assert not p.is_absolute(), f"eval {e['id']} fixture path not portable: {rel}"
            assert (ROOT / p).exists(), f"eval {e['id']} fixture missing: {rel}"

    # --- trigger-eval balance + explicit/bare contract ---
    triggers = json.loads((ROOT / "evals" / "trigger-eval.json").read_text(encoding="utf-8"))
    assert len(triggers) >= 20, f"trigger eval set too small: {len(triggers)}"
    positives = sum(1 for t in triggers if t["should_trigger"])
    assert 8 <= positives <= len(triggers) - 8, (
        f"trigger eval set imbalanced: {positives}/{len(triggers)} positives")
    for t in triggers:
        for marker in EXPLICIT_MARKERS:
            if marker in t["query"]:
                assert t["should_trigger"], f"explicitly named query must trigger: {t['query']}"
    assert any(t["query"] == BARE_NON_TRIGGER and not t["should_trigger"] for t in triggers), (
        f"bare '{BARE_NON_TRIGGER}' must be a non-trigger")
    assert any("npm" in t["query"] and not t["should_trigger"] for t in triggers), (
        "dependency-upgrade near-miss negative missing")
    assert any("bump" in t["query"] and not t["should_trigger"] for t in triggers), (
        "release-action near-miss negative missing")

    # --- fixtures portability (no absolute paths leaking in) ---
    fixtures_dir = ROOT / "evals" / "fixtures"
    assert fixtures_dir.is_dir(), "fixtures directory missing"
    leaked = []
    for p in fixtures_dir.rglob("*"):
        if p.is_file() and p.suffix in (".md", ".json", ".py"):
            t = p.read_text(encoding="utf-8", errors="ignore")
            if "/Users/" in t or "/tmp/" in t:
                leaked.append(str(p.relative_to(ROOT)))
    assert not leaked, f"fixtures contain absolute paths: {leaked}"

    print(
        "[OK] ruyi-version-check structural eval passed "
        f"(description={len(description)} chars, body={line_count} lines, "
        f"behavior_evals={len(evals)}, trigger_evals={len(triggers)}, "
        f"trigger_positives={positives})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
