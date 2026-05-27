# Verification Report: Zod v4 Walkthrough (Round 9)

**Date:** 2026-05-08
**Source:** `examples/_src_zod/` (Zod v4.4.3)
**Output:** `examples/zod-r9/docs/`
**Reviewer:** Independent verification pass

## Issues Found and Fixed

### Issue 1: `// Source:` with wrong line range (07-api-factories.md, _string)
- **Location:** 07-api-factories.md line 9
- **Problem:** Code block cited `api.ts:63-71` but included `// @__NO_SIDE_EFFECTS__` comment from line 62, which was outside the cited range.
- **Fix:** Updated range to `api.ts:62-71`.
- **Severity:** Medium (Source: tag was inaccurate)

### Issue 2: `// Source:` on simplified code (05-checks-system.md, $ZodCheckOverwrite)
- **Location:** 05-checks-system.md line 171
- **Problem:** Code block was marked `// Source:` but was simplified -- the actual source spans lines 1217-1226 with different formatting: multi-line constructor call, type annotation `<$ZodCheckOverwrite>`, extra blank lines.
- **Fix:** Changed to `// Simplified from: packages/zod/src/v4/core/checks.ts:1217-1226`.
- **Severity:** Medium (Source: tag on non-verbatim code)

### Issue 3: `// Source:` with wrong line range (07-api-factories.md, _email)
- **Location:** 07-api-factories.md line 30
- **Problem:** Same pattern as Issue 1. Cited `api.ts:96-107` but included `// @__NO_SIDE_EFFECTS__` from line 95.
- **Fix:** Updated range to `api.ts:95-107`.
- **Severity:** Medium

### Issue 4: `// Source:` with wrong line range (07-api-factories.md, _int)
- **Location:** 07-api-factories.md line 54
- **Problem:** Same pattern. Cited `api.ts:606-617` but included annotation from line 605.
- **Fix:** Updated range to `api.ts:605-617`.
- **Severity:** Medium

### Issue 5: `// Source:` with wrong line range (07-api-factories.md, _lt)
- **Location:** 07-api-factories.md line 78
- **Problem:** Same pattern. Cited `api.ts:857-867` but included annotation from line 856.
- **Fix:** Updated range to `api.ts:856-867`.
- **Severity:** Medium

### Issue 6: `// Source:` on simplified code (07-api-factories.md, _positive etc.)
- **Location:** 07-api-factories.md line 97
- **Problem:** Code block was marked `// Source:` but heavily simplified -- collapsed multi-line functions with full type annotations and `@__NO_SIDE_EFFECTS__` comments into single-line forms without types.
- **Fix:** Changed to `// Simplified from:` and removed the `@__NO_SIDE_EFFECTS__` comment from the code block.
- **Severity:** Medium

### Issue 7: Count claim wrong in manifest (claim-023)
- **Location:** sources-manifest.json claim-023
- **Problem:** Claimed "31 check functions" but actual count is 30 (29 `_` prefixed exports + 1 `type` export).
- **Fix:** Updated to "30 items" and noted the type export.
- **Severity:** Low (count error in manifest only, doc text was not specific about count)

### Issue 8: Manifest line ranges exceeded file lengths (5 claims)
- **Location:** sources-manifest.json claims 002, 008, 012, 024, 026
- **Problem:** Line ranges were set 1 line beyond actual file lengths (e.g., `[1, 5]` for a 4-line file).
- **Fix:** Corrected all ranges to exact file lengths.
- **Severity:** Low (caught by verify script)

## Verification Checks Performed

### Code Block Citations (all 20 Source: tags checked)
- 13 verbatim blocks: diff'd against source lines, all match exactly after fixes
- 7 Simplified blocks: confirmed they contain structural/content differences from source

### Version Exact Match
- `packages/zod/package.json`: `"version": "4.4.3"` -- matches doc
- `packages/zod/src/v4/core/versions.ts`: `major: 4, minor: 4, patch: 3` -- matches doc

### Directory Structure
- `packages/`: verified by `ls` -- 8 directories as listed
- `packages/zod/src/v4/`: verified by `ls` -- classic, core, mini, locales, index.ts as described
- `packages/zod/src/v4/core/`: verified by `ls` -- all files listed in table confirmed
- `packages/zod/src/v4/classic/`: verified by `ls` -- all files listed confirmed
- `packages/zod/src/v4/mini/`: verified by `ls` -- all files listed confirmed

### API Signatures
- `$ZodIssueBase` fields (code?, input?, path, message): verified exact match
- `$ZodCheckDef` fields (check, error?, abort?, when?): verified exact match
- `ZodMiniType` methods (parse, safeParse, parseAsync, safeParseAsync, check, with, clone, register, brand, def, apply): verified exact match
- `ZodType` methods: verified all listed methods exist in interface (parse, safeParse, encode, decode, optional, nullable, transform, pipe, etc.)

### Architecture Claims
- Classic does NOT import from mini (verified: grep for "mini" in classic/ found only "minimum" and one test file)
- Mini does NOT import from classic (verified: grep for "classic" in mini/ found nothing)
- Both import from core (verified: both external.ts files import from `../core/index.js`)

### Line Ranges
- All 28 claims with source_lines re-checked against actual file line counts
- All ranges now within file bounds

### Count Claims
- `$ZodIssue` union: 11 types -- verified by counting `|` lines in source
- `$ZodStringFormats` union: 30 values -- verified by counting `|` lines in source
- `$ZodChecks` union: 15 types -- verified by counting `|` lines in source
- classic/checks.ts re-exports: 30 items -- verified by `grep -c`
- core/schemas.ts: 4730 lines -- verified by `wc -l`

## Post-Fix Verification

- `python3 scripts/verify_sources.py examples/zod-r9/docs/sources-manifest.json --source-dir examples/_src_zod` -- ALL CHECKS PASSED
- All `// Source:` blocks re-verified as verbatim via `diff`
- All `// Simplified from:` blocks confirmed as non-verbatim

## Final Status

ZERO ISSUES REMAINING after fixes -- CLEAN ROUND

All 8 issues found during independent verification were fixed before final validation.
