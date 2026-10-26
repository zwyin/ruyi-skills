#!/usr/bin/env bash
# install.sh — One-command installer: copy ruyi-skills into local agent skill roots
#
# Usage:
#   ./scripts/install.sh [--agent claude|codex|all] [--skill <name>|all]
#                        [--list] [--uninstall] [--force]
#
#   Defaults: --agent all (detected: ~/.claude exists -> claude,
#             ~/.codex exists -> codex) x --skill all
#   Targets:  ~/.claude/skills/<name>/ and ~/.codex/skills/<name>/
#   Copy range: outer skills/<name>/ whole dir (nested skills/<n>/ preserved for
#             marketplace-layout compat). Dev artifacts, local tool state and
#             repo metadata excluded — top level of the skill dir:
#             tests/ evals/ debug/ cursor/ dist/; at any depth (dirs):
#             __pycache__/ .playwright-mcp/ ruyi_project_study_*/ project_study_*/
#             .pytest_cache/ .codegraph/ .claude/ .opencode/ .windsurf/ .github/;
#             at any depth (files): .DS_Store .gitignore.
#   Idempotency: content diff ignoring the .ruyi-install marker ->
#             "installed:" / "skip (up-to-date):" / "updated:"
#   --uninstall: only removes targets that carry the .ruyi-install marker AND
#             still match the source; refuses otherwise unless --force.
#
# Known limitations (per-skill standalone install):
#   1. 合集级共享引用（如 safe-publish 的 ../../../scripts/check_update.sh）只在
#      整仓安装（marketplace/插件方式）下可解析。
#   2. version-check SKILL.md 的指令是仓库根相对路径
#      （python3 skills/ruyi-version-check/scripts/...），per-skill 安装后从
#      用户项目 cwd 不可解析。
#   3. walkthrough 顶层 SKILL.md 的 ../../scripts/、../../docs/、references/
#      引用只有嵌套内层副本自洽，agent 从顶层加载时悬空——walkthrough 完整体验
#      推荐 marketplace 安装。
#
# No network access; bash + coreutils only.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"
MARKER=".ruyi-install"
# Top-level (skill-dir root) dev-artifact dirs to strip after copy.
TOP_EXCLUDES="tests evals debug cursor dist"
# Any-depth directory name patterns to strip after copy: dev artifacts plus
# local tool state / repo metadata (.codegraph holds a LIVE unix socket —
# GNU cp errors on it under set -e, aborting the install mid-run). Quoted
# array literals: never word-split or glob-expanded (an unquoted
# "project_study_*" would be pathname-expanded against the cwd first).
DEPTH_EXCLUDE_DIRS=(
    '__pycache__'
    '.playwright-mcp'
    'ruyi_project_study_*'
    'project_study_*'
    '.pytest_cache'
    '.codegraph'
    '.claude'
    '.opencode'
    '.windsurf'
    '.github'
)
# Any-depth file name patterns to strip after copy.
DEPTH_EXCLUDE_FILES=('.DS_Store' '.gitignore')

AGENT="" # empty = auto-detect (all detected agents)
SKILL="" # empty = all
LIST=0
UNINSTALL=0
FORCE=0
STAGING=""
REFUSED=0

usage() {
    sed -n '2,32p' "$0" | sed 's/^# \{0,1\}//'
}

die() {
    echo "error: $*" >&2
    exit 1
}

cleanup() {
    [ -n "$STAGING" ] && [ -d "$STAGING" ] && rm -rf "$STAGING" || true
}
trap cleanup EXIT

# --- skills ---

installable_skills() {
    local d
    for d in "$SKILLS_DIR"/*/; do
        [ -f "${d}SKILL.md" ] || continue
        basename "$d"
    done
}

is_installable() {
    [ -n "$1" ] && [ -f "$SKILLS_DIR/$1/SKILL.md" ]
}

# Build a pristine install image of <skill> under a fresh staging dir:
# whole-dir copy with excludes stripped, no marker. Echo the image path.
build_staging() {
    local skill="$1" img
    [ -d "$STAGING" ] || STAGING="$(mktemp -d "${TMPDIR:-/tmp}/ruyi-install.XXXXXX")"
    img="$STAGING/$skill"
    [ -d "$img" ] && rm -rf "$img"
    cp -R "$SKILLS_DIR/$skill" "$img"
    local pat
    # any-depth dir patterns (prune: never descend into a match)
    local dir_args=()
    for pat in "${DEPTH_EXCLUDE_DIRS[@]}"; do
        dir_args+=(-name "$pat" -o)
    done
    unset "dir_args[${#dir_args[@]}-1]" # drop trailing -o
    find "$img" -type d \( "${dir_args[@]}" \) -prune -exec rm -rf {} +
    # any-depth file patterns
    local file_args=()
    for pat in "${DEPTH_EXCLUDE_FILES[@]}"; do
        file_args+=(-name "$pat" -o)
    done
    unset "file_args[${#file_args[@]}-1]" # drop trailing -o
    find "$img" -type f \( "${file_args[@]}" \) -delete
    # top-level patterns
    local d
    for d in $TOP_EXCLUDES; do
        rm -rf "$img/$d"
    done
    echo "$img"
}

# --- agents ---

agent_root() { # claude|codex -> skills root
    echo "$HOME/.$1/skills"
}

detected_agents() {
    local agents=""
    [ -d "$HOME/.claude" ] && agents="claude"
    [ -d "$HOME/.codex" ] && agents="$agents codex"
    echo "$agents"
}

resolve_agents() {
    # Sets global AGENTS (word list).
    if [ "$AGENT" = "claude" ] || [ "$AGENT" = "codex" ]; then
        AGENTS="$AGENT"
        return 0
    fi
    AGENTS="$(detected_agents)"
    if [ -z "$AGENTS" ]; then
        die "no agent detected (~/.claude and ~/.codex both absent); use --agent claude|codex to force"
    fi
}

resolve_skill() {
    # Sets global SKILLS (word list) or exits 1.
    if [ -z "$SKILL" ] || [ "$SKILL" = "all" ]; then
        SKILLS="$(installable_skills)"
        [ -n "$SKILLS" ] || die "no installable skills found under $SKILLS_DIR"
        return 0
    fi
    if ! is_installable "$SKILL"; then
        echo "error: unknown skill '$SKILL'" >&2
        echo "available skills:" >&2
        local s
        for s in $(installable_skills); do echo "  $s" >&2; done
        exit 1
    fi
    SKILLS="$SKILL"
}

# --- per-target operations ---

same_content() { # <pristine-img> <target> -> 0 iff identical ignoring marker
    diff -rq -x "$MARKER" "$1" "$2" >/dev/null 2>&1
}

install_one() { # <agent> <skill>
    local agent="$1" skill="$2" root tgt img
    root="$(agent_root "$agent")"
    tgt="$root/$skill"
    img="$(build_staging "$skill")"

    if [ -d "$tgt" ]; then
        if same_content "$img" "$tgt"; then
            echo "skip (up-to-date): $agent/$skill"
            return 0
        fi
        rm -rf "$tgt"
        local action="updated"
    else
        local action="installed"
    fi
    mkdir -p "$root"
    mv "$img" "$tgt"
    {
        echo "source: $SKILLS_DIR/$skill"
        echo "agent: $agent"
        echo "date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } >"$tgt/$MARKER"
    echo "$action: $agent/$skill"
}

uninstall_one() { # <agent> <skill>
    local agent="$1" skill="$2" root tgt
    root="$(agent_root "$agent")"
    tgt="$root/$skill"

    if [ ! -d "$tgt" ]; then
        echo "not installed: $agent/$skill"
        return 0
    fi
    if [ ! -f "$tgt/$MARKER" ]; then
        if [ "$FORCE" = "1" ]; then
            rm -rf "$tgt"
            echo "removed (forced, no marker): $agent/$skill"
        else
            echo "refuse: $agent/$skill has no $MARKER marker (not installed by install.sh); use --uninstall --force to delete" >&2
            REFUSED=1
        fi
        return 0
    fi
    local img clean=0
    img="$(build_staging "$skill")"
    # capture the verdict BEFORE rm -rf destroys the evidence
    same_content "$img" "$tgt" && clean=1
    if [ "$clean" = "1" ] || [ "$FORCE" = "1" ]; then
        rm -rf "$tgt"
        if [ "$clean" = "1" ]; then
            echo "removed: $agent/$skill"
        else
            echo "removed (forced, modified): $agent/$skill"
        fi
    else
        echo "refuse: $agent/$skill differs from source (locally modified?); use --uninstall --force to delete" >&2
        REFUSED=1
    fi
}

list_all() {
    local s agents a
    echo "skills:"
    for s in $(installable_skills); do
        echo "  $s"
    done
    echo "agents:"
    agents="$(detected_agents)"
    for a in claude codex; do
        if printf '%s\n' "$agents" | grep -qw "$a"; then
            echo "  $a ($(agent_root "$a")) [detected]"
        else
            echo "  $a ($(agent_root "$a")) [not detected]"
        fi
    done
}

# --- args ---

while [ $# -gt 0 ]; do
    case "$1" in
    --agent)
        [ $# -ge 2 ] || die "--agent requires a value (claude|codex|all)"
        AGENT="$2"
        shift 2
        ;;
    --skill)
        [ $# -ge 2 ] || die "--skill requires a value (<name>|all)"
        SKILL="$2"
        shift 2
        ;;
    --list) LIST=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --force) FORCE=1; shift ;;
    -h | --help) usage; exit 0 ;;
    *) usage; die "unknown argument: $1" ;;
    esac
done

case "$AGENT" in
"" | claude | codex | all) ;;
*) die "--agent must be claude, codex, or all (got: $AGENT)" ;;
esac

[ -d "$SKILLS_DIR" ] || die "skills directory not found: $SKILLS_DIR"

if [ "$LIST" = "1" ]; then
    list_all
    exit 0
fi

resolve_agents
resolve_skill

for agent in $AGENTS; do
    for skill in $SKILLS; do
        if [ "$UNINSTALL" = "1" ]; then
            uninstall_one "$agent" "$skill"
        else
            install_one "$agent" "$skill"
        fi
    done
done

exit "$REFUSED"
