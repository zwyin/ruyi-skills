# Skill Architecture Review: Why Rules Failed and What to Do Instead

**Date**: 2026-05-08
**Scope**: Structural analysis of the project-walkthrough skill after 12 rounds of accuracy enforcement
**Core question**: Is "more rules" the right architecture, or does the skill need a fundamentally different approach?

---

## 0. The Numbers

The skill specification currently consists of:

| File | Lines | Role |
|------|-------|------|
| SKILL.md | 400 | Main skill definition + 6 accuracy rules + Phase 3A/3B/3C procedure |
| exploration-protocol.md | 161 | Phase 1 exploration steps |
| sources-manifest-schema.md | 161 | Manifest JSON schema |
| accuracy-verification-protocol.md | 162 | Verification checklist |
| chapter-templates.md | 199 | Chapter structure per project type |
| html-reference.md | 308 | HTML generation spec |
| verify_sources.py | 310 | Automated verification script |
| test_walkthrough_output.py | 539 | 157 automated tests |

**Total specification: ~2,240 lines** governing a process that generates 6-15 markdown files.

The 12-round verification history:

| Rounds | Action Taken | Result |
|--------|-------------|--------|
| 1-3 | Added 6 accuracy rules + manifest + verify script | Still failed on fabricated code, wrong counts, wrong architecture |
| 3-4 | Restructured Phase 3 into manifest-first (3A/3B/3C) | Line range and labeling issues remained |
| 4-8 | Added verification rules for counts, imports, line ranges | Source vs Simplified labeling still wrong (35 issues in bat alone) |
| 8-9 | Added more granular Phase 3A instructions | Still 8 self-corrections needed |
| 9-10 | Banned `// Source:` tag entirely | First zero-issue round |

Every single intervention was "add a rule" or "add a verification step." The question is whether this is sustainable.

---

## 1. Root Cause Analysis: Why Rules Keep Getting Broken

### 1.1 The LLM Compliance Ceiling

The fundamental problem is not that the rules are bad. The rules are mostly correct -- the final 8 rules in the "Accuracy Rules (MANDATORY)" section and the Phase 3A verification checklist are sound advice. The problem is that **LLM compliance with rules degrades as rule count and complexity increase**.

This is well-documented behavior. LLMs do not have a "rule engine." Rules are tokens in the context window. When there are 18+ imperative directives scattered across 400 lines, the model does not uniformly weight them. Instead:

- **Rules near the generation point** (the text being produced right now) are weighted higher.
- **Rules buried in the middle of long instruction blocks** are weighted lower.
- **Rules that conflict with the model's training prior** (e.g., "write plausible code examples" vs "never invent code") are systematically underweighted.

The evidence: 35 Source/Simplified mislabelings in bat across rounds 5 and 8. The rule "mark as Simplified if you changed anything" was present and clear. The model simply did not follow it 35 times, because its training prior says "Source: means this is where it comes from" and it defaults to that.

### 1.2 The Verification Paradox

Phase 3C asks the LLM to verify its own output. But the same cognitive limitations that caused the errors in Phase 3B prevent reliable detection in Phase 3C:

- If the model thought a code block was verbatim when writing it (hence labeled `// Source:`), it will likely still think it's verbatim when re-reading it. The blind spot is persistent.
- Self-correction works only when the error is conspicuous enough to break through the model's confidence. Off-by-one line ranges (claiming lines 1-8 in a 7-line file) are caught because the verification script flags them externally. Subtle simplifications (indentation removed, comments omitted) are not caught because the model doesn't perceive them as errors.

The rounds where self-correction worked best (rounds 10-12) were rounds where the rules had already eliminated the error categories entirely (banning Source:, mandating conservative line ranges). Self-correction was unnecessary because the structural changes prevented the errors from occurring.

### 1.3 The Wrong Abstraction Level

The skill treats accuracy as a compliance problem ("follow these rules"). But accuracy failures are not primarily compliance failures. They are **process architecture** failures:

1. **The writing process has no checkpoint.** Phase 3 says "verify before write" but the LLM naturally wants to produce text. The verification step is a speed bump, not a gate. The model reads the rule, nods, and proceeds to write first and verify later.

2. **The manifest is treated as documentation, not as a build artifact.** The manifest should be the output of a compilation step that produces a binary artifact. Instead, it's freeform JSON that the model generates alongside the prose. There is no compiler enforcing its correctness.

3. **The verification script runs after generation, not during.** `verify_sources.py` is excellent, but it runs in Phase 5 (verify) or Phase 3C (validate coverage). By that point, errors are baked into prose. The script catches them, but fixing them requires re-reading source files and re-editing chapters -- expensive and unreliable.

---

## 2. Structural vs Rule-Based Enforcement: The Right Comparison

### 2.1 Definitions

- **Rule-based enforcement**: "Do X." The LLM is told what to do and trusted to comply. Failure mode: the LLM doesn't comply.
- **Structural enforcement**: The process is designed so that X happens automatically, or X is impossible to skip. Failure mode: the process itself has a bug (but this is rarer and more fixable).

### 2.2 What Worked: The One Structural Success

The manifest-first architecture (Phase 3A before 3B) is the only structural enforcement in the current skill. It says: you must produce a JSON manifest with verified claims BEFORE you write any prose.

This is partially structural. It creates an artifact (the manifest) that can be checked by a script. But it is still rule-based in practice because:

- The model generates the manifest itself (no external compiler).
- There is no hard gate preventing Phase 3B from starting before 3A is complete.
- The "Hard rule: If a claim is NOT in the manifest..." is still just a rule.

Compare this to a truly structural approach: a bash script that reads the manifest and refuses to output the markdown files until the manifest passes validation. That would be structurally impossible to bypass. The current approach relies on the LLM to self-enforce.

### 2.3 The Banning of `// Source:` as Structural

Banning the `// Source:` tag and mandating `// Simplified from:` for all code blocks is the most effective single change made during the 12 rounds. It eliminated 35+ errors across bat rounds alone.

Why it worked is instructive. It did NOT work because the model became more careful about labeling. It worked because it **removed a choice point**. Before the ban, the model had to decide for each code block: "Is this verbatim or simplified?" This decision was wrong ~50% of the time. After the ban, there is no decision. All code blocks are `Simplified from:`. The error category ceases to exist.

This is structural enforcement through **choice elimination**, not rule compliance. The model cannot make the wrong labeling choice because the choice has been removed.

---

## 3. Five Structural Changes

Each change follows the same principle: remove a decision point where the LLM can make an error, or add a mechanical gate that is enforced by something other than the LLM's compliance.

### 3.1 Split Phase 3A Into a Separate Script-Enforced Step

**Current**: Phase 3A is a set of instructions in SKILL.md telling the LLM to verify claims and build a manifest before writing.

**Proposed**: Extract Phase 3A into a standalone bash-script protocol.

```
Step 1: LLM produces a "claims plan" JSON file listing intended claims
        (file path, claim type, but NO source_lines yet)

Step 2: A bash script reads each planned claim, reads the source file,
        and outputs the actual content/line count for LLM to cite

Step 3: LLM fills in the manifest using ONLY data from Step 2 output

Step 4: verify_sources.py runs on the manifest
        (this already exists, just moved earlier)

Step 5: If Step 4 passes, LLM may proceed to Phase 3B (writing)
```

The bash script in Step 2 would be something like:

```bash
#!/bin/bash
# For each planned claim, extract actual source data
# Input: claims-plan.json
# Output: verified-claims.json (with real line numbers, content snippets)

jq -r '.claims[] | "\(.source_file)\t\(.type)"' claims-plan.json | \
while IFS=$'\t' read -r srcfile claim_type; do
    if [ ! -f "$SOURCE_DIR/$srcfile" ]; then
        echo "FILE_NOT_FOUND: $srcfile"
        continue
    fi
    total_lines=$(wc -l < "$SOURCE_DIR/$srcfile")
    echo "FILE_OK: $srcfile ($total_lines lines)"
done
```

This is not a full solution (the LLM still needs to identify the right line ranges), but it creates a mechanical checkpoint: **every source file's existence and line count is confirmed by a script before the manifest is finalized**. The LLM cannot claim a file exists without the script confirming it. It cannot claim lines 1-65 in a 64-line file because the script reports the line count.

**What errors this prevents**: fabricated file paths, line ranges exceeding file length, version numbers from stale sources.

**What it does NOT prevent**: wrong line ranges that are within file bounds (claiming lines 42-58 when the actual code is at 44-60), fabricated content that happens to be in a real file. These require deeper structural changes.

**Complexity cost**: One new ~50-line bash script. No change to the LLM's core task. The script is a gate, not a participant.

### 3.2 Mandate `wc -l` and `grep -c` for All Quantitative Claims

**Current**: The rules say "count the ACTUAL items" and suggest using vague language for large files. The LLM is trusted to count.

**Proposed**: Replace all counting instructions with a mechanical protocol:

```
Before writing any quantitative claim ("N types", "N files", "N variants"):
1. Generate the appropriate shell command
2. Run it
3. Use the output as the claim value

Commands:
- File count:    ls src/*.rs | wc -l
- Type count:    grep -c 'export type\|export interface' src/index.ts
- Enum variants: grep -c '|' path/to/enum.ts (after reading to confirm it's an enum)
- Directory entries: ls -1 dir/ | wc -l
- Lines in file: wc -l path/to/file.ts
```

Make this part of Phase 3A's output format. Each manifest entry for a quantitative claim must include a `count_command` and `count_output` field:

```json
{
  "id": "claim-023",
  "type": "architecture_claim",
  "claim_summary": "classic/checks.ts re-exports 30 check functions",
  "count_command": "grep -c 'export' packages/zod/src/v4/classic/checks.ts",
  "count_output": "30",
  "verified": true
}
```

**What errors this prevents**: All count estimation errors (round 3's "32 types" vs actual 40, round 9's "31 check functions" vs actual 30).

**Complexity cost**: Adds 2 fields to the manifest schema. The LLM generates a shell command, runs it, and records the output. This is a mechanical operation, not a judgment call.

### 3.3 Pre-Generate Architecture Diagrams From Import Data

**Current**: The LLM draws architecture diagrams based on its understanding, then verifies each arrow against imports. Verification is a rule, not a gate.

**Proposed**: Add an architecture discovery script step that generates the diagram skeleton:

```bash
#!/bin/bash
# Extract actual import dependencies between top-level modules
# Input: source directory
# Output: dependency-graph.txt (adjacency list)

for dir in src/*/; do
    module=$(basename "$dir")
    imports=$(grep -rh "from '\.\." "$dir" | \
              sed "s/.*from '\.\.\///" | \
              cut -d'/' -f1 | \
              sort -u | \
              tr '\n' ',' | \
              sed 's/,$//')
    if [ -n "$imports" ]; then
        echo "$module -> $imports"
    fi
done
```

Output would look like:
```
classic -> core
mini -> core
core -> (none)
```

The LLM then draws the diagram from this data, not from directory structure. If the data says classic imports from core but not from mini, the diagram MUST show them as parallel siblings.

**What errors this prevents**: The Zod classic->mini->core chain error (round 3). Any architecture diagram error caused by directory-structure-based inference.

**Complexity cost**: One ~20-line bash script. The LLM's diagram-drawing task is unchanged -- it just uses different (script-verified) input.

### 3.4 Make Phase 3B a Template-Fill Operation, Not Free Writing

**Current**: Phase 3B says "write the chapter" using verified claims. This is freeform writing, which is where the LLM introduces errors by adding unverified details, embellishments, and "helpful" context.

**Proposed**: Restrict Phase 3B's output format so that every factual statement must be tagged with its manifest ID:

```markdown
## Core Schema Types

Zod defines [claim-015] approximately 40 type literals in `$ZodTypeDef.type`,
consolidated into a single file `core/schemas.ts` [claim-016] spanning 4,730 lines.

<!-- code:claim-017 -->
// Simplified from: packages/zod/src/v4/core/schemas.ts:39-78
type $ZodTypeDef =
  | { type: "string"; ... }
  | { type: "number"; ... }
  ...

The classic layer [claim-018] wraps these core types with a method-chaining API.
```

A post-processing step (bash script) then:
1. Extracts all `[claim-NNN]` references
2. Confirms each exists in the manifest with `verified: true`
3. Confirms every manifest entry is referenced in at least one chapter
4. Flags any code block without a `<!-- code:claim-NNN -->` annotation

**What errors this prevents**: Unverified claims sneaking into prose (the most common Phase 3B error). The LLM can still write fluent prose, but every factual anchor must have a manifest backlink.

**Complexity cost**: Adds `[claim-NNN]` annotations to the writing format (minor visual noise). A ~40-line bash script for cross-referencing. The manifest already exists -- this just adds bidirectional linking.

### 3.5 Collapse the Rule Sections Into the Process Steps

**Current**: SKILL.md has:
- 6 "Accuracy Rules (MANDATORY)" in a separate section after Phase 3
- Detailed inline rules within Phase 3A's verification checklist
- More rules in the "Source Verification (MANDATORY)" section under Documentation Standards
- Yet more rules in the Checklist section

The same directives appear 2-3 times in different wording. For example:
- Rule 1 "No invented code" repeats the Phase 3A instruction "Code block: Read the actual source file..."
- Rule 3 "Verify before stating" repeats the Phase 3A instruction "Read the source files..."
- The Documentation Standards section repeats Rule 2 about citing source files

**Proposed**: Delete the separate "Accuracy Rules" section entirely. Delete the "Source Verification" section under Documentation Standards. Keep ONLY the process steps (Phase 3A, 3B, 3C), and make each step specific enough that the rules are embedded in the procedure.

The principle: **a rule that is part of a step is followed; a rule that is a standalone imperative is ignored**.

Revised Phase 3A step 2 (example):

```
2. Read the source files -- For each planned claim:

   a. Code block: Run `cat -n source_file | sed -n 'START,ENDp'`
      - If the output doesn't match what you planned, STOP and adjust
      - Record the EXACT line range from the cat output
      - Tag: code_example

   b. Directory structure: Run `ls -1 directory/`
      - Copy the output, do not paraphrase
      - Tag: directory_structure

   c. Version number: Run `grep '"version"' package.json`
      - Use the exact value from the output
      - Tag: version_number

   d. API signature: Run `grep -A5 'function name\|def name\|fn name' source_file`
      - Use the actual definition, not the call site
      - Tag: api_signature

   e. Count claim: Run the appropriate count command (see protocol)
      - Record command and output
      - Tag: architecture_claim
```

Each sub-step includes the mechanical verification command. The rule is not "verify before stating" -- it is "run this command and use its output." The rule IS the step.

**What errors this prevents**: Rule blindness caused by having too many standalone directives. By embedding the verification into the step itself, the LLM never reaches a "now write the claim" point without having already verified it mechanically.

**Complexity cost**: SKILL.md gets shorter (delete ~40 lines of duplicated rules). Phase 3A gets slightly longer (more specific step instructions). Net change is roughly zero.

---

## 4. Why These Changes Work (And Previous Ones Didn't)

### The pattern in successful vs unsuccessful interventions

| Intervention | Type | Errors Eliminated | Why It Worked |
|---|---|---|---|
| Manifest-first (3A before 3B) | Structural (partial) | Fabricated content | Creates a checkpoint artifact |
| Ban `// Source:` | Structural (choice elimination) | All labeling errors | Removes the decision point |
| File-size aware reading | Rule | Large-file estimation errors | LLM sometimes follows it |
| Count claim tiers | Rule | Some count errors | LLM sometimes follows it |
| Import verification for arch diagrams | Rule | Some diagram errors | LLM sometimes follows it |

The two interventions that eliminated entire error categories were structural. The four that reduced but did not eliminate errors were rule-based.

### The proposed changes continue this pattern

| Change | Error Category Eliminated | Mechanism |
|---|---|---|
| Script-enforced Phase 3A | Fabricated paths, off-by-one line ranges | External gate |
| Mandatory count commands | All count estimation errors | Mechanized counting |
| Import graph script | Architecture diagram inference errors | Data-driven diagram |
| Template-fill with claim IDs | Unverified claims in prose | Bidirectional linking |
| Rules collapsed into steps | Rule blindness | No standalone rules to ignore |

### What these changes do NOT address

1. **Wrong line ranges within file bounds** (claiming lines 42-58 when the code is at 44-60). The script confirms the file is 200 lines long, but the LLM still picks the range. Fixing this would require extracting code snippets by content matching, which is possible but adds significant complexity.

2. **Subtle code simplification that changes semantics** (removing a `?` error handler, changing a generic type parameter). The `Simplified from:` label covers this, but the reader may not realize the simplification changed behavior. Fixing this would require diff-based verification, which is beyond what bash scripts can reliably do.

3. **Omission errors** (important details left out because the LLM didn't read the right files). No structural fix for this -- the exploration protocol is the best tool, and it is already rule-based by necessity.

These remaining error categories are inherently judgment-dependent. They cannot be eliminated by structural changes because they require understanding code semantics. The goal should be to reduce them to a low baseline, not eliminate them.

---

## 5. What NOT to Do

### 5.1 Do Not Add More Rules

The skill already has 18+ imperative directives across 400 lines. Adding a 19th will not help. The LLM's compliance ceiling has been reached. Round 10-12's success came from structural changes (banning Source:, manifest-first), not from the additional rules added in rounds 5-9.

### 5.2 Do Not Make the Process More Verbose

SKILL.md is already 400 lines. The total specification is 2,240 lines. Each additional line of instruction dilutes the attention given to every other line. The proposed changes should REPLACE existing sections, not add to them.

### 5.3 Do Not Add a "Self-Review" Pass

Phase 3C already serves this purpose, and it catches only the errors that are externally conspicuous (line ranges exceeding file bounds, missing manifest entries). Adding another review pass would add time without adding accuracy, because the same cognitive blind spots that caused the errors in Phase 3B persist in Phase 3C.

### 5.4 Do Not Try to Enforce Verbatim Code

The `// Source:` vs `// Simplified from:` saga proved that verbatim enforcement does not work. The LLM always simplifies (removes indentation, omits comments, adjusts formatting). The structural fix was to accept this reality and mandate `Simplified from:` universally. Re-introducing any form of verbatim requirement would re-introduce the same error category.

---

## 6. Recommended Implementation Order

| Priority | Change | Effort | Impact |
|---|---|---|---|
| 1 | Collapse rules into process steps (3.5) | Low (restructure SKILL.md) | Reduces rule blindness immediately |
| 2 | Mandatory count commands with manifest fields (3.2) | Low (add 2 fields + instructions) | Eliminates count errors |
| 3 | Script-enforced Phase 3A gate (3.1) | Medium (new bash script) | Eliminates path/range fabrication |
| 4 | Template-fill with claim IDs (3.4) | Medium (format change + script) | Eliminates unverified claim leakage |
| 5 | Import graph script for architecture (3.3) | Low (new bash script) | Eliminates diagram inference errors |

Priority 1 and 2 can be done immediately with text edits. Priority 3-5 require new scripts but are independent -- they can be implemented in any order.

---

## 7. Conclusion

The 12-round verification history tells a clear story: **rules reduced errors but never eliminated them; structural changes eliminated entire error categories**. The skill's accuracy problem is not a compliance problem -- it is an architecture problem.

The five proposed changes share a single principle: **replace LLM judgment calls with mechanical operations wherever possible**. The LLM is excellent at writing fluent prose, identifying interesting patterns, and explaining code. It is unreliable at counting accurately, labeling correctly, remembering line numbers, and resisting the urge to embellish. The structural changes keep the LLM in its strength zone (prose, analysis, explanation) and move its weakness zone (verification, counting, labeling) into scripts and mechanical protocols.

The skill should aim to be the thinnest possible instruction layer on top of mechanical verification. Every rule that can be replaced by a script should be. Every decision point that can be removed should be. The remaining rules should be embedded in process steps, not stated as standalone imperatives.

The goal is not zero rules. It is zero rules that the LLM routinely breaks.
