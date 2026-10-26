"""
tests/test_install_sh.py — Validate scripts/install.sh behavior

Contract under test (task-12 brief):
  install.sh [--agent claude|codex|all] [--skill <name>|all] [--list] [--uninstall] [--force]

  - default = all detected agents (~/.claude -> claude, ~/.codex -> codex) x all skills
  - copy range = outer skills/<name>/ whole dir, nested skills/<n>/ preserved,
    dev artifacts excluded (tests/ evals/ debug/ cursor/ dist/ at skill-dir top
    level; __pycache__/ .playwright-mcp/ ruyi_project_study_*/ project_study_*/
    at any depth)
  - idempotency via diff ignoring the .ruyi-install marker:
    absent -> "installed:", identical -> "skip (up-to-date):", differs -> "updated:"
  - --uninstall only removes marker-managed, unmodified targets; refuses otherwise
    unless --force

Test isolation: every subprocess runs with HOME pointed at a pytest tmp dir —
the real HOME is never touched. Two script sources are used:
  1. the real repo script + real skills/ (read-only source; wiring check);
  2. a sandbox repo (script copied + synthetic skills) for mutation tests
     (source modification must never touch the real repo tree).
"""

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "install.sh"
REAL_SKILLS = [
    "ruyi-github-safe-publish",
    "ruyi-project-walkthrough",
    "ruyi-version-check",
]


def run_script(script, args, home, timeout=300):
    """Run install.sh with HOME overridden to a fake home; never the real one."""
    env = dict(os.environ)
    env["HOME"] = str(home)
    assert env["HOME"] != os.path.expanduser("~"), "test must not use real HOME"
    return subprocess.run(
        ["bash", str(script)] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(Path(script).resolve().parent.parent),
        env=env,
    )


def make_home(tmp_path, agents=("claude",), name="home"):
    home = tmp_path / name
    home.mkdir(exist_ok=True)
    for agent in agents:
        (home / f".{agent}").mkdir(exist_ok=True)
    return home


@pytest.fixture
def sandbox(tmp_path):
    """Fake repo: real script copy + synthetic skills with a full junk layout."""
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    shutil.copy2(SCRIPT, repo / "scripts" / "install.sh")

    alpha = repo / "skills" / "alpha"
    (alpha / "scripts").mkdir(parents=True)
    (alpha / "SKILL.md").write_text("---\nname: alpha\n---\nalpha body\n")
    (alpha / "scripts" / "tool.py").write_text("print('tool')\n")
    nested = alpha / "skills" / "alpha"  # nested inner copy must be preserved
    (nested / "__pycache__").mkdir(parents=True)
    (nested / "__pycache__" / "x.pyc").write_bytes(b"\x00")
    (nested / "SKILL.md").write_text("---\nname: alpha\n---\nalpha body\n")
    (nested / "tests" / "inner_test.py").parent.mkdir(parents=True)
    (nested / "tests" / "inner_test.py").write_text("# inner copy keeps its tests\n")
    for junk in (
        "tests",
        "evals",
        "debug",
        "cursor",
        "dist",
        ".playwright-mcp",
        "ruyi_project_study_junk",
        "project_study_junk",
    ):
        (alpha / junk).mkdir()
        (alpha / junk / "artifact.txt").write_text("dev artifact\n")
    (alpha / "scripts" / "__pycache__").mkdir()
    (alpha / "scripts" / "__pycache__" / "t.pyc").write_bytes(b"\x00")

    beta = repo / "skills" / "beta"
    beta.mkdir(parents=True)
    (beta / "SKILL.md").write_text("---\nname: beta\n---\nbeta body\n")

    home = make_home(tmp_path)
    return {
        "repo": repo,
        "script": repo / "scripts" / "install.sh",
        "home": home,
        "alpha_src": alpha / "SKILL.md",
        "run": lambda args, h=None: run_script(
            repo / "scripts" / "install.sh", args, h or home
        ),
    }


# --- real-repo wiring (source read-only) ---


class TestRealRepoInstall:
    def test_script_is_executable(self):
        assert os.access(str(SCRIPT), os.X_OK), "install.sh should be executable"

    def test_default_install_then_rerun_all_skip(self, tmp_path):
        home = make_home(tmp_path, agents=("claude",))
        r1 = run_script(SCRIPT, [], home)
        assert r1.returncode == 0, r1.stderr
        out1 = r1.stdout
        for name in REAL_SKILLS:
            assert f"installed: claude/{name}" in out1, out1
            skill_dir = home / ".claude" / "skills" / name
            assert (skill_dir / "SKILL.md").is_file(), f"missing {name}/SKILL.md"
            marker = skill_dir / ".ruyi-install"
            assert marker.is_file(), f"missing marker for {name}"
            marker_text = marker.read_text()
            assert "source:" in marker_text and "date:" in marker_text, marker_text
        # outer-dir copy proof: scripts/ ships (inner nested copy lacks it)
        vc = home / ".claude" / "skills" / "ruyi-version-check"
        assert (vc / "scripts" / "validate_versions.py").is_file()
        # nested inner copy preserved
        pw = home / ".claude" / "skills" / "ruyi-project-walkthrough"
        assert (pw / "skills" / "ruyi-project-walkthrough" / "SKILL.md").is_file()
        # no updated/skip on first run
        assert "updated:" not in out1 and "skip" not in out1

        r2 = run_script(SCRIPT, [], home)
        assert r2.returncode == 0, r2.stderr
        for name in REAL_SKILLS:
            assert f"skip (up-to-date): claude/{name}" in r2.stdout, r2.stdout
        assert "installed:" not in r2.stdout and "updated:" not in r2.stdout

    def test_real_repo_excludes_stripped_from_targets(self, tmp_path):
        home = make_home(tmp_path, agents=("claude",))
        r = run_script(SCRIPT, [], home)
        assert r.returncode == 0, r.stderr
        vc = home / ".claude" / "skills" / "ruyi-version-check"
        assert not (vc / "tests").exists(), "tests/ must not ship"
        assert not (vc / "evals").exists(), "evals/ must not ship"
        pw = home / ".claude" / "skills" / "ruyi-project-walkthrough"
        for top in ("debug", "cursor", "dist", "tests", "evals"):
            assert not (pw / top).exists(), f"{top}/ must not ship"
        # any-depth patterns: source has scripts/__pycache__ and study dirs
        assert not list(pw.rglob("__pycache__")), "no __pycache__ at any depth"
        assert not list(pw.rglob("project_study_*")), "no project_study_*/ at any depth"
        assert not list(pw.rglob("ruyi_project_study_*"))
        assert not (pw / ".playwright-mcp").exists()
        # nested inner copy keeps its own tests/ (marketplace layout compat)
        nested_tests = pw / "skills" / "ruyi-project-walkthrough" / "tests"
        if nested_tests.exists():
            assert nested_tests.is_dir()


class TestRealRepoCliGuards:
    def test_unknown_skill_errors(self, tmp_path):
        home = make_home(tmp_path)
        r = run_script(SCRIPT, ["--skill", "no-such-skill"], home)
        assert r.returncode != 0
        combined = r.stdout + r.stderr
        assert "no-such-skill" in combined
        for name in REAL_SKILLS:
            assert name in combined, "error should list available skills"

    def test_invalid_agent_rejected(self, tmp_path):
        home = make_home(tmp_path)
        r = run_script(SCRIPT, ["--agent", "gemini"], home)
        assert r.returncode != 0

    def test_list_shows_skills_and_agents(self, tmp_path):
        home = make_home(tmp_path, agents=("claude",))
        r = run_script(SCRIPT, ["--list"], home)
        assert r.returncode == 0, r.stderr
        for name in REAL_SKILLS:
            assert name in r.stdout
        assert "claude" in r.stdout
        assert "codex" in r.stdout  # listed even when not detected

    def test_no_agent_detected_errors_with_hint(self, tmp_path):
        home = make_home(tmp_path, agents=())
        r = run_script(SCRIPT, [], home)
        assert r.returncode != 0
        assert "--agent" in (r.stdout + r.stderr)


# --- sandbox behavior tests (mutation-safe) ---


class TestSandboxInstallLifecycle:
    def test_install_includes_scripts_and_nested_copy(self, sandbox):
        r = sandbox["run"]([])
        assert r.returncode == 0, r.stderr
        tgt = sandbox["home"] / ".claude" / "skills" / "alpha"
        assert (tgt / "scripts" / "tool.py").is_file()
        assert (tgt / "skills" / "alpha" / "SKILL.md").is_file()

    def test_excludes_absent_in_target(self, sandbox):
        r = sandbox["run"]([])
        assert r.returncode == 0, r.stderr
        tgt = sandbox["home"] / ".claude" / "skills" / "alpha"
        for top in ("tests", "evals", "debug", "cursor", "dist", ".playwright-mcp",
                    "ruyi_project_study_junk", "project_study_junk"):
            assert not (tgt / top).exists(), f"{top}/ leaked into target"
        assert not list(tgt.rglob("__pycache__")), "__pycache__ leaked at depth"
        # nested inner copy survives (incl. its own tests/)
        assert (tgt / "skills" / "alpha" / "tests" / "inner_test.py").is_file()

    def test_source_modified_then_updated(self, sandbox):
        r1 = sandbox["run"](["--skill", "alpha"])
        assert r1.returncode == 0, r1.stderr
        assert "installed: claude/alpha" in r1.stdout
        sandbox["alpha_src"].write_text(
            "---\nname: alpha\n---\nalpha body v2\n"
        )
        r2 = sandbox["run"](["--skill", "alpha"])
        assert r2.returncode == 0, r2.stderr
        assert "updated: claude/alpha" in r2.stdout, r2.stdout
        tgt = sandbox["home"] / ".claude" / "skills" / "alpha"
        assert "alpha body v2" in (tgt / "SKILL.md").read_text()
        assert (tgt / ".ruyi-install").is_file()

    def test_single_skill_flag_installs_only_that_skill(self, sandbox):
        r = sandbox["run"](["--skill", "alpha"])
        assert r.returncode == 0, r.stderr
        skills_root = sandbox["home"] / ".claude" / "skills"
        assert (skills_root / "alpha").is_dir()
        assert not (skills_root / "beta").exists()


class TestSandboxAgents:
    def test_both_agents_detected_installs_to_both(self, sandbox, tmp_path):
        home = make_home(tmp_path, agents=("claude", "codex"), name="home-both")
        r = sandbox["run"]([], home)
        assert r.returncode == 0, r.stderr
        for agent in ("claude", "codex"):
            assert f"installed: {agent}/alpha" in r.stdout, r.stdout
            assert (home / f".{agent}" / "skills" / "alpha" / "SKILL.md").is_file()

    def test_codex_only_detected(self, sandbox, tmp_path):
        home = make_home(tmp_path, agents=("codex",), name="home-codex")
        r = sandbox["run"]([], home)
        assert r.returncode == 0, r.stderr
        assert "installed: codex/alpha" in r.stdout
        assert (home / ".codex" / "skills" / "alpha").is_dir()
        assert not (home / ".claude").exists(), "must not create undetected agent dir"

    def test_explicit_agent_forces_undetected_target(self, sandbox, tmp_path):
        home = make_home(tmp_path, agents=(), name="home-empty")
        r = sandbox["run"](["--agent", "claude"], home)
        assert r.returncode == 0, r.stderr
        assert "installed: claude/alpha" in r.stdout
        assert (home / ".claude" / "skills" / "alpha").is_dir()


class TestSandboxUninstall:
    def test_uninstall_removes_clean_target(self, sandbox):
        assert sandbox["run"]([]).returncode == 0
        r = sandbox["run"](["--uninstall"])
        assert r.returncode == 0, r.stderr
        assert "removed: claude/alpha" in r.stdout, r.stdout
        assert "removed: claude/beta" in r.stdout
        assert not (sandbox["home"] / ".claude" / "skills" / "alpha").exists()
        assert not (sandbox["home"] / ".claude" / "skills" / "beta").exists()

    def test_uninstall_not_installed_is_noop(self, sandbox):
        r = sandbox["run"](["--uninstall"])
        assert r.returncode == 0, r.stderr
        assert "not installed: claude/alpha" in r.stdout, r.stdout

    def test_uninstall_refuses_user_modified_then_force_deletes(self, sandbox):
        assert sandbox["run"]([]).returncode == 0
        tgt = sandbox["home"] / ".claude" / "skills" / "alpha" / "SKILL.md"
        tgt.write_text("---\nname: alpha\n---\nuser edited\n")
        r = sandbox["run"](["--uninstall"])
        assert r.returncode != 0, "must refuse to delete user-modified target"
        combined = r.stdout + r.stderr
        assert "refuse" in combined.lower()
        assert "--force" in combined
        assert tgt.exists(), "refused uninstall must leave target in place"
        r2 = sandbox["run"](["--uninstall", "--force"])
        assert r2.returncode == 0, r2.stderr
        assert not tgt.parent.exists()

    def test_uninstall_refuses_target_without_marker_then_force(self, sandbox):
        assert sandbox["run"]([]).returncode == 0
        alpha_dir = sandbox["home"] / ".claude" / "skills" / "alpha"
        (alpha_dir / ".ruyi-install").unlink()  # simulate foreign directory
        r = sandbox["run"](["--uninstall"])
        assert r.returncode != 0, "must refuse unmanaged target"
        combined = r.stdout + r.stderr
        assert ".ruyi-install" in combined, "message must explain the marker check"
        assert alpha_dir.exists()
        r2 = sandbox["run"](["--uninstall", "--force"])
        assert r2.returncode == 0, r2.stderr
        assert not alpha_dir.exists()
