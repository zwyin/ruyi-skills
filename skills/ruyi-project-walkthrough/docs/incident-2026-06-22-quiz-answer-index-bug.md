# Incident Report 2026-06-22: Quiz Answer Index Always Collapsed to Option A

**Bug:** `md_to_html.py` `parse_quiz_md` extracted the answer letter with `re.search(r'([A-D])', line)`, which matched the literal `A` inside the word `Answer` instead of the real answer letter. Every quiz question's correct index collapsed to `0` (option A) regardless of the actual answer — picking A was always judged correct; picking the real answer was judged wrong.

**Impact:** All 11 affected walkthrough reports (under `repo_ds1600`) generated with `--quiz-chapter` since 2026-05-27 (commit `ca1f371`) had wrong quiz answers. Two follow-on issues uncovered during fix: (1) `check_update.sh` cache falsely prompted "new version" pointing backwards right after users upgraded the plugin (same root cause: stale SHA comparison); (2) `parse_quiz_md` was appending the inter-question `---` separator into the preceding explanation's text.

**Fix strategy:** Single-line regex anchor change in `parse_quiz_md` + a `---` early-stop in explanation collection. Cover four propagation channels in sequence (dev repo → brand repos via `brand-sync-tool` → local Claude Code plugin via `/plugin` → local agents via direct copy). Replace manual `release.sh` (broken under collection architecture — assumes repo-root paths and requires `develop` branch) with manual 7-place version bump. Each fix ships as its own patch release (v0.9.1/2/3) so users can update incrementally.

**Defense in depth:** Add `tests/test_quiz_parsing.py` with regression coverage across all answer letters (A/B/C/D), Chinese colon, and mixed-answer quizzes. The existing `test_html_quiz_answer_index_valid` only checked `0 ≤ c < len(opts)` and missed the bug — it should also verify the source-vs-HTML SHA/answer-letter match. Tighten `parse_quiz_md` with an anchor so the regex can only match the intended letter, not substring noise.

**Reviewed end-to-end by** independent verification at every propagation step (real quiz source → real HTML regeneration → c-values match markdown Answer letters).

---

## 1. Background & Scope

### 1.1 What is `parse_quiz_md`?

`scripts/md_to_html.py`'s `parse_quiz_md` parses the `## Quiz` section of a walkthrough chapter markdown file (per SKILL.md L541-572 spec). Output is a `quizData` JS array embedded in the generated HTML — each item is `{q, o, c, e}` for question text, options, correct-index, explanation. The HTML's interactive quiz widget highlights `o[c]` as the correct option.

```python
# --- 2. Check cache (skip if checked within 24h) --- ...
def parse_quiz_md(quiz_md):
    ...
    for line in lines:
        opt_match = re.match(r'^(?:[-*]\s+)?([A-D])[.)]\s+(.*)', line)
        if opt_match and state in ("question", "options"):
            state = "options"
            opts.append(opt_match.group(2))
        elif re.match(r'^\*\*Answer\s*[：:]\s*[A-D]\s*\*\*', line, re.IGNORECASE):
            # FIXED: anchor the letter search
            m = re.search(r'[：:]\s*([A-D])\s*\*\*', line, re.IGNORECASE)
            if m: answer = m.group(1).upper()
            state = "answer"
        elif re.match(r'^\*\*Explanation\s*[：:]', line, re.IGNORECASE):
            ...
```

### 1.2 How it broke

The original answer-extraction step was a two-statement pair:

```python
elif re.match(r'^\*\*Answer\s*[：:]\s*[A-D]\s*\*\*', line, re.IGNORECASE):
    m = re.search(r'([A-D])', line, re.IGNORECASE)   # ← bug
    if m: answer = m.group(1).upper()
    state = "answer"
```

The `re.match(...)` correctly gates on the `**Answer: X**` shape, but `re.search(r'([A-D])', line)` then scans the **whole line** for the first A-D letter. For any `**Answer: B**`-shaped line, the first A-D letter is the `A` inside the literal word `Answer` (position 2), not the real answer letter (position 10+). So `answer` was always `"A"`, `correct = ord('A') - ord('A') = 0`.

This bug was introduced in commit `ca1f371` (2026-05-27). Every report generated with `--quiz-chapter` from that point on had every quiz question's `c=0`.

### 1.3 Why the test suite missed it

`tests/test_walkthrough_output.py::test_html_quiz_answer_index_valid` only asserts:

```python
if not isinstance(correct, int) or correct < 0 or correct >= len(opts):
    errors.append(...)
```

It checks the **shape** of the answer index (`0 ≤ c < len(opts)`) but never **cross-checks** `c` against the source markdown's `**Answer: X**` letter. With `c=0` always, the shape test passed forever.

The 3 test fixtures under `tests/fixtures/*/interactive/walkthrough.html` were built before `--quiz-chapter` existed (DOM-based legacy), so none exercised `parse_quiz_md`. There was zero direct unit test coverage of `parse_quiz_md`.

### 1.4 User-reported reproduction

User generated a walkthrough for `repo_ds1600/github_individual_follow_naizhao/...deep-zh-general`. Quiz Q1: "这个项目的核心数据管线顺序是?" Correct answer should be B (per the explanation text: "配置定义目标→采集器抓数据→存到 data→分析器处理→生成报告"). Selecting B produced an error; selecting A produced "correct". The user reported this on 2026-06-22, triggering this incident.

---

## 2. Root Cause (One-liner)

`re.search(r'([A-D])', line)` in `parse_quiz_md` is not anchored to the answer letter position — it matches the `A` inside the literal word `Answer`, collapsing every quiz's correct index to 0.

---

## 3. Fix

### 3.1 Code change (1 line of regex)

**File:** `skills/ruyi-project-walkthrough/scripts/md_to_html.py` L247

**Before:**
```python
m = re.search(r'([A-D])', line, re.IGNORECASE)
```

**After:**
```python
# Anchor the letter search to "after the colon, before the closing **" so we
# capture the answer letter, not the 'A' in the literal word "Answer".
# re.search(r'([A-D])', ...) on the whole line always matched that 'A' first
# → every c collapsed to 0 regardless of the real answer.
m = re.search(r'[：:]\s*([A-D])\s*\*\*', line, re.IGNORECASE)
```

The replacement regex `r'[：:]\s*([A-D])\s*\*\*'` anchors between the colon (`: / ：`) and the closing `**`. It only matches when the letter is flanked by these markers — can't be fooled by the `A` in `Answer`.

### 3.2 Companion fix: explanation `---` swallowing

While auditing other lines in `parse_quiz_md`, noticed the explanation collector was appending the inter-question `---` separator into the preceding question's explanation text (visible in HTML as each explanation trailing with ` ---`).

**File:** `skills/ruyi-project-walkthrough/scripts/md_to_html.py` L253-254

```python
elif state == "explanation":
    # `---` is the inter-question separator; stop collecting so it
    # does not get appended to the explanation text.
    if line.strip() == "---":
        break
    explanation += " " + line
```

### 3.3 Test coverage

**New file:** `skills/ruyi-project-walkthrough/tests/test_quiz_parsing.py` — 7 test cases:
- `test_answer_b_yields_index_1` (the core regression)
- `test_answer_a_yields_index_0` (the case that previously masked the bug)
- `test_answer_c_yields_index_2`
- `test_answer_d_yields_index_3`
- `test_answer_with_chinese_colon` (`**Answer：C**`)
- `test_mixed_answers_across_questions` (realistic quiz with letters B/D/A/C)
- `test_explanation_and_question_preserved`

Pre-fix: 6 fail / 1 pass (only the A case passed by accident). Post-fix: 7 pass.

---

## 4. Follow-on Discovery: `check_update.sh` Cache Edge Case

The SessionStart hook (added in v0.9.2, see §5.2) made a pre-existing latent bug in `scripts/check_update.sh` user-visible. Symptom: right after `claude plugin update ruyi-skills@ruyi-skills`, the next SessionStart would output a fake "🔄 有新版本可用（NEW_LOCAL → OLD_CACHED_REMOTE）" prompt pointing backwards.

**Root cause:** `check_update.sh` L48-56 replays the cached `remoteSha` whenever it differs from `LOCAL_SHA`, without noticing that `LOCAL_SHA` itself may have changed (i.e. user upgraded).

**Fix:** Cache now stores `localShaAtCheck`. Replay only fires when the current `LOCAL_SHA == localShaAtCheck`. If they differ (user upgraded in the meantime), the cache is treated as stale → script re-checks the remote instead of replaying backwards. Backward compatible (old caches without the field are treated as stale → re-check).

---

## 5. Propagation Chain

Once the dev repo had the fix, it had to reach 4 downstream channels. Each step verified before moving to the next.

### 5.1 Channel A: Stock 11 affected reports in `repo_ds1600`

User asked to *audit only*, not to regenerate. Audit findings: 11 reports under `repo_ds1600` had `c=0` for every quiz question (`article_archieve_claude` ×7, `github_individual_follow_naizhao` ×1, `claude-md-manager` ×1, `gz-ai-chat-eval-toolkit` ×1, `llm-benchmark-claude` ×1).

User later authorized regeneration. All 11 regenerated with the fixed converter. Per-report safety pattern: backup `.bak` → regenerate (overwrite) → verify `c` values match markdown Answer letters + `verify-result.json` passed → commit `.bak` removal or rollback. **11/11 succeeded, zero rollbacks.**

### 5.2 Channel B: Brand repos (paoding / davinci / doraemon)

User requirement: "ensure consistent experience for all direct installers" → fix must land in the brand repos (not just ruyi).

**Discovery:** `md_to_html.py` exists in **17 locations**. Only 1 (dev repo) is fixed; 15 others (brand repos via `brand-sync`, installed Claude Code plugin, installed agents) carry the same source bug.

**brand-sync mechanism:** `brand-sync-tool/sync.sh` rsyncs from `ruyi-skills` to each brand `output/{brand}/` (pushes to that brand's GitHub repo). L96 `RSYNC_EXCLUDES` does not exclude `scripts/` — `scripts/md_to_html.py` propagates. L264-273 Step 9a brand-replaces `REPO=` and `PLUGIN_KEY=` lines in `scripts/check_update.sh`.

**Verified locally:** `bash sync.sh --dry-run` reproduced 11/11 propagation success (paoding `d24de66`, davinci `59140fe`, doraemon `1256a10` — each `sync: update from ruyi-skills @ fb5b066`).

**Push:** Removed `--dry-run`, retried on network failures. **paoding `43816c0`, davinci `697a42c`, doraemon `76acef2`** all pushed to `zwyin/{brand}-skills.git`. Each `sync: update from ruyi-skills @ b204bd4` (and later `181ca23`).

### 5.3 Channel C: Local Claude Code plugin

`~/.claude/plugins/marketplaces/ruyi-skills` is a git clone of `zwyin/ruyi-skills`. User ran `/plugin` reinstall → cache updated to `b204bd4` (v0.9.2) and later `181ca23` (v0.9.3). Verified: `installed_plugins.json` `gitCommitSha` = latest, `hooks/session-start` runs on every SessionStart and emits valid JSON `additionalContext`.

### 5.4 Channel D: Local agents skill (`~/.agents/skills/{4品牌}`)

4 brand `walkthrough` skill copies under `~/.agents/skills/` were still BUG-version. Mounted into agent containers via `_agents.mount_config: /mnt/host/.../.agents:/mnt/.agents` — no git, no install script (likely copied manually). No plugin-management command available.

**Update mechanism:** `md_to_html.py` contains brand strings (`tool_name` / `tool_url` defaults, 6-line diff per brand). Cannot copy from ruyi directly → must copy from each brand's sync output. From `brand-sync-tool/output/{brand}/skills/{brand}-project-walkthrough/scripts/md_to_html.py` (v0.9.3, brand-replaced, quiz-fixed) → `~/.agents/skills/{brand}-project-walkthrough/scripts/md_to_html.py`. **4/4 updated; brand strings preserved; quiz fixed.**

### 5.5 Channel E: Dead-remnant cleanup

Full-disk scan found 18 `md_to_html.py` copies. After all four propagation channels above:
- **10 fixed** (all runtime paths)
- **8 still BUG**, classified:

| Type | Count | Disposition |
|------|-------|-------------|
| Old plugin cache (`a44ad7433343`, `fcaedc33cf26`) | 2 | Dead — `installed_plugins` points to `b204bd4`. **Removed** (careful `rm`). |
| Archived marketplace (`project-walkthrough-skill`) | 1 | Dead — not installed, registered in `~/.claude/plugins/known_marketplaces.json`. **Removed registration entry then `rm` directory**. |
| `4_compare/{4品牌}/` (brand output diff snapshots) | 4 | **Intentionally preserved** — these are the user's brand-comparison reference. Updating them would defeat their purpose. |
| `~/repo_skillforge/project-walkthrough-skill/` | 1 | **Intentionally preserved** — archived pre-collection source repo. Not maintained. |

User explicitly authorized the cleanup of the 3 dead remnants (vs. preserving them) via AskUserQuestion. After cleanup: 5 BUG-version copies remain on disk, all with documented intent. **Zero BUG copies are reachable by any runtime path.**

---

## 6. Versioning & Release

### 6.1 Why three releases in one day

Each release addressed a distinct concern, so users could update incrementally rather than wait for a bundled big-bang:

| Version | Date | Skill | Collection | What |
|---------|------|-------|------------|------|
| v0.9.1 | 2026-06-22 | 1.6.1→1.6.2 | 0.9.0→0.9.1 | Quiz answer-index fix (PR#10) |
| v0.9.2 | 2026-06-22 | 1.6.2→1.6.3 | 0.9.1→0.9.2 | SessionStart auto update-check hook |
| v0.9.3 | 2026-06-22 | 1.6.3→1.6.4 | 0.9.2→0.9.3 | `check_update.sh` cache false-prompt fix |

### 6.2 `release.sh` is broken under the collection architecture

`skills/ruyi-project-walkthrough/scripts/release.sh` (designed for the pre-collection layout) computes `ROOT = scripts/..` and then reads `skills/ruyi-project-walkthrough/SKILL.md` relative to `ROOT`. Under the current ruyi-skills collection layout that resolves to `skills/ruyi-project-walkthrough/skills/ruyi-project-walkthrough/SKILL.md` (does not exist). It also gates on `branch == develop` (we're on `main`).

**Workaround used for all three releases:** Manual 7-place version bump + `bash scripts/convert.sh --all && --check` + `pytest tests/` + commit + push + tag. Test assertions in `test_lang_output.py` are dynamic (read SKILL.md frontmatter), so they automatically follow the bump — no test edits needed.

A proper fix to `release.sh` (or a `release-collection.sh`) is **out of scope** for this incident and remains a follow-up.

### 6.3 Release artifact locations

All 4 repos (ruyi-skills + 3 brand repos) received each release on `main` + git tag `v0.9.X`:

| Repo | v0.9.1 commit | v0.9.2 commit | v0.9.3 commit |
|------|---------------|---------------|---------------|
| ruyi-skills | `fb5b066` | `b204bd4` | `181ca23` |
| paoding-skills | `a4e99d7` | `43816c0` | `67b9ff3` |
| davinci-skills | `c8ae722` | `697a42c` | `eadfc74` |
| doraemon-skills | `256c5a5` | `76acef2` | `9d3a9f4` |

All commits on `main` branches. All tags pushed.

---

## 7. Verification Matrix

| Verification | Result |
|--------------|--------|
| Unit tests (`tests/test_quiz_parsing.py`) | 7/7 pass |
| Full test suite (`pytest tests/` in skill) | 292 pass, 23 skipped (no regression) |
| Full test suite (`pytest tests/` in collection root) | 18/18 pass |
| `make ci` locally | Pass |
| `bash scripts/convert.sh --check` | ✓ both skills |
| `python3 scripts/check_self_contained.py` | OK |
| Marketplace JSON validity | OK |
| CI on PR#10 (7 jobs across macOS/Ubuntu/Python 3.10/3.12) | All SUCCESS |
| End-to-end on real quiz source (naizhao 16 questions) | c-values = `[B,C,A,B,B,A,C,B,B,C,B,B,C,B,B,B]` matches markdown ground truth |
| brand-sync --dry-run 3 brands | hooks propagated; `check_update.sh` REPO/PLUGIN_KEY brand-replaced correctly |
| `hooks/session-start` JSON output | Valid JSON, `additionalContext` populated only when upgrade available |
| Full-disk scan after cleanup | 10 fixed + 5 intentionally preserved (zero runtime-reachable BUG copies) |

---

## 8. Defense in Depth

Future regressions of the same shape are now blocked by three layers:

1. **Direct unit test:** `test_quiz_parsing.py` exercises `parse_quiz_md` with all 4 answer letters + Chinese colon + multi-question quizzes. Pre-fix: 6/7 fail. Post-fix: 7/7 pass.
2. **Anchored regex:** The fix changes the extraction regex from `re.search(r'([A-D])', line)` to `re.search(r'[：:]\s*([A-D])\s*\*\*', line)`. The new pattern *requires* the letter to be between the colon and the closing `**` — it cannot be confused with the `A` in `Answer`. Future careless edits to drop the anchors would re-introduce the bug, and the unit test would catch it.
3. **Process:** The existing `test_html_quiz_answer_index_valid` only checked shape (`0 ≤ c < len(opts)`), which is why this bug shipped in the first place. Recommendation for follow-up: tighten it to also assert that the `c` value corresponds to the source markdown's `**Answer: X**` letter for a real markdown source (cross-check, not just shape). This was the original gap.

---

## 9. What was deliberately not done (and why)

- **4_compare and archived source `md_to_html.py`** — User confirmed they are intentional reference snapshots (brand diff / archived history). Updating them would defeat their purpose. They are now documented as "intentionally preserved" in `memory/quiz-bug-regen-followup.md`.
- **Fixing `release.sh` itself** — It's broken under the collection architecture, but fixing it is a separate refactor outside this incident's scope. The manual 7-place bump worked but is brittle. Recommend a follow-up issue.
- **`/plugin update` for the user's local v0.9.2 → v0.9.3** — User-managed; cannot be automated from the agent side. User is notified in the incident close.
- **Agents skill `SKILL.md` version + `check_update.sh` cache fix propagation** — Low priority; agents containers may or may not honor them. Out of scope for the quiz-answer correctness incident.

---

## 10. Timeline (2026-06-22)

- **Bug reported** by user (naizhao walkthrough, Q1 quiz answer wrong).
- **Root cause located** in `md_to_html.py:247` (regex anchored to wrong position).
- **PR#10** opened (`fb5b066`), CI green, merged.
- **11 affected reports regenerated** in `repo_ds1600`.
- **4 propagation channels** completed: dev repo → brand-sync → Claude Code plugin → agents.
- **v0.9.1 / v0.9.2 / v0.9.3** shipped to all 4 repos.
- **3 dead remnants cleaned up** (old caches + archived marketplace).
- **Final disk scan:** 10 fixed + 5 intentionally preserved (zero runtime-reachable BUG copies).
- **Total elapsed:** single working day.

---

## 11. Cross-references

- PR: [#10](https://github.com/zwyin/ruyi-skills/pull/10) — `fix(walkthrough): quiz correct-answer index always collapsed to option A`
- Commit: `fb5b066` (v0.9.1 root fix)
- CHANGELOG: `skills/ruyi-project-walkthrough/CHANGELOG.md` entries `[1.6.2]`, `[1.6.3]`, `[1.6.4]`
- Test file (new): `skills/ruyi-project-walkthrough/tests/test_quiz_parsing.py`
- Companion docs: `docs/fix-proposal-empty-html.md` (similar structure — bug → root cause → fix strategy → defense-in-depth)
- SessionStart hook mechanism: see the SessionStart hook spec at `~/.claude/plugins/marketplaces/ruyi-skills/skills/ruyi-project-walkthrough/hooks/hooks.json` + `hooks/session-start`
- Cross-session memory: `memory/quiz-bug-regen-followup.md`, `memory/ruyi-skills-update-check-hook.md`
