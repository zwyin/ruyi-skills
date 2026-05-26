# Verification Report: Zod v4 Walkthrough (Round 12 / zod-r12)

**Date**: 2026-05-08
**Verifier**: Independent verification pass (strictest possible)
**Source**: `examples/_src_zod/`
**Output**: `examples/zod-r12/docs/`
**Manifest**: `examples/zod-r12/docs/sources-manifest.json`

---

## Verification Checklist

### 1. Code Block Attribution Format
- **Check**: ALL code blocks must use `// Simplified from:` prefix
- **Result**: 31 instances of `// Simplified from:` across 30 fenced code blocks
- **Result**: ZERO instances of `// Source:` found
- **PASS**

### 2. Line Range Validity
- **Check**: ALL `source_lines` end values must be <= total file lines
- **Result**: All 40 claims verified. Every source_lines range validated against actual file.
- **Method**: Python script checked all 40 claims against actual file line counts
- **PASS**

### 3. Version Exact Match
- **Check**: Version must match `packages/zod/package.json` exactly
- **Source**: `"version": "4.4.3"` (line 4 of package.json)
- **Walkthrough**: States "Zod v4.4.3" and "version is 4.4.3"
- **Also verified**: `packages/zod/src/v4/core/versions.ts` has `{major:4, minor:4, patch:3}`
- **PASS**

### 4. Directory Structure Verified
- **Check**: `v4/classic/` has schemas.ts and checks.ts, NOT individual type files
- **Result**: `ls v4/classic/` shows: checks.ts, coerce.ts, compat.ts, errors.ts, external.ts, from-json-schema.ts, index.ts, iso.ts, parse.ts, schemas.ts, tests/
- **Check**: `v4/mini/` has parallel structure
- **Result**: `ls v4/mini/` shows: checks.ts, coerce.ts, external.ts, index.ts, iso.ts, parse.ts, schemas.ts, tests/
- **Check**: `v4/core/` has the engine files
- **Result**: Confirmed api.ts, checks.ts, core.ts, errors.ts, parse.ts, schemas.ts, util.ts, etc.
- **PASS**

### 5. API Signatures Match Source Exactly
- **$constructor interface**: Source lines 7-10 match walkthrough
- **$ZodTypeDef**: Source lines 50-94 match walkthrough description
- **$ZodCheckDef**: Source lines 11-18 match walkthrough (check, error, abort, when)
- **$ZodIssueBase**: Source lines 10-15 have exactly code, input, path, message -- walkthrough lists only these
- **$ZodError**: Source lines 219-228 have type, issues, _zod, stack, name -- walkthrough correctly shows this
- **$ZodConfig**: Source lines 124-131 have customError, localeError, jitless -- walkthrough shows all three
- **_string factory**: Source lines 63-72 match walkthrough exactly
- **Classic ZodType interface**: Source lines 78-210 match walkthrough's method list
- **PASS**

### 6. Architecture Claims Backed by Imports
- **Claim**: "Classic and mini are parallel siblings over core"
  - Classic `schemas.ts` line 1: `import * as core from "../core/index.js"`
  - Mini `schemas.ts` line 1: `import * as core from "../core/index.js"`
  - **Verified**
- **Claim**: "Root index re-exports from v4/classic"
  - `src/index.ts` line 1: `import * as z from "./v4/classic/external.js"`
  - **Verified**
- **Claim**: "Mini re-exports core directly"
  - `mini/external.ts` exports core directly
  - **Verified**
- **PASS**

### 7. Count Claims Accuracy
- **"11 concrete issue types"**: Source $ZodIssue union at line 180-191 has 11 members
  (InvalidType, TooBig, TooSmall, InvalidStringFormat, NotMultipleOf, UnrecognizedKeys, InvalidUnion, InvalidKey, InvalidElement, InvalidValue, Custom)
  - **Verified**: exact count is 11
- **"25+ format methods"**: ZodString has 22 format method attachments + regex/includes/startsWith/endsWith/lowercase/uppercase from _ZodString = ~28 total
  - **Verified**: "25+" is accurate
- **"dozens" vague claims**: Walkthrough uses "dozens of format validation methods" which is safe
- **PASS**

### 8. Manifest Entries Have Valid doc_file + doc_line
- **Check**: All 40 claims reference `docs/walkthrough.md` which exists
- **Check**: Maximum doc_line referenced is 295, walkthrough has 609 lines
- **PASS**

### 9. verify_sources.py Script
- **Result**: `All checks passed` (zero errors, zero warnings)
- **PASS**

---

## Summary

| Check | Result |
|-------|--------|
| Code blocks use `// Simplified from:` | PASS (31/30) |
| No `// Source:` found | PASS (0 instances) |
| All line ranges valid | PASS (40/40) |
| Version exact match | PASS (4.4.3) |
| Directory structure verified | PASS |
| API signatures match source | PASS |
| Architecture backed by imports | PASS |
| Count claims accurate | PASS |
| Manifest doc_file/doc_line valid | PASS |
| verify_sources.py | PASS |

---

**ZERO ISSUES -- CLEAN ROUND -- TERMINATION CONDITION MET**
