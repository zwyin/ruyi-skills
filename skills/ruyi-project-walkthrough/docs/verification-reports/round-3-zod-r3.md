# Verification Report: Zod Walkthrough (Round 3, zod-r3)

**Date**: 2026-05-07
**Walkthrough**: `examples/zod-r3/docs/`
**Source**: `examples/_src_zod/` (Zod 4.4.3)
**Reviewer**: Independent accuracy reviewer

---

## Check 1: Code Example Existence

**Method**: For every code block in all 6 walkthrough files, locate the `// Source:` citation, navigate to the actual source file, verify file existence, line range validity, and content match.

### Results

| Doc File | Line | Citation | File Exists | Lines Valid | Content Match |
|----------|------|----------|-------------|-------------|---------------|
| 01-overview.md | 14 | package.json:9 | YES | YES | YES |
| 01-overview.md | 26 | package.json:5 | YES | YES | YES |
| 01-overview.md | 35 | package.json:36-47 | YES | YES | YES (zshy.exports matches) |
| 01-overview.md | 61 | core/index.ts:1-16 | YES | YES | YES |
| 01-overview.md | 86 | mini/external.ts:1-8 | YES | YES | YES |
| 01-overview.md | 99 | classic/external.ts:1-12 | YES | YES | YES |
| 01-overview.md | 125 | core/versions.ts:1-5 | YES | YES | YES (exact match) |
| 02-type-system.md | 10 | core/core.ts:17-21 | YES | YES | YES (exact match) |
| 02-type-system.md | 23 | core/core.ts:68-74 | YES | YES | YES (exact match) |
| 02-type-system.md | 41 | core/schemas.ts:179-186 | YES | YES | YES (exact match) |
| 02-type-system.md | 55 | core/schemas.ts:168-173 | YES | YES | YES (exact match) |
| 02-type-system.md | 67 | core/schemas.ts:96-166 | YES | YES | YES (simplified with `(...)`) |
| 02-type-system.md | 94 | core/schemas.ts:50-94 | YES | YES | YES (exact match) |
| 02-type-system.md | 116 | core/schemas.ts:190-208 | YES | YES | YES (exact match) |
| 02-type-system.md | 145 | core/schemas.ts:357-377 | YES | YES | YES (exact match) |
| 02-type-system.md | 175 | core/schemas.ts:1637-1678 | YES | PARTIAL | SEE ISSUE 1 |
| 02-type-system.md | 205 | core/schemas.ts:34-44 | YES | YES | YES (exact match) |
| 03-validation-engine.md | 12 | core/parse.ts:16-28 | YES | YES | YES (exact match) |
| 03-validation-engine.md | 40 | core/parse.ts:59-72 | YES | YES | YES (exact match) |
| 03-validation-engine.md | 59 | classic/parse.ts:4-6 | YES | YES | YES (exact match) |
| 03-validation-engine.md | 70 | core/parse.ts:39-51 | YES | YES | YES (exact match) |
| 03-validation-engine.md | 91 | core/parse.ts:103-106 | YES | YES | YES (exact match) |
| 03-validation-engine.md | 105 | core/schemas.ts:278-295 | YES | YES | YES (simplified with `// ...`) |
| 03-validation-engine.md | 131 | core/schemas.ts:16-25 | YES | YES | YES (exact match) |
| 03-validation-engine.md | 145 | core/schemas.ts:28-32 | YES | YES | YES (exact match) |
| 03-validation-engine.md | 158 | core/parse.ts:30 | YES | YES | YES (exact match) |
| 03-validation-engine.md | 168 | classic/parse.ts:8-13 | YES | YES | YES (exact match) |
| 04-schema-types.md | 10 | classic/schemas.ts:78-93 | YES | YES | YES (simplified with `// ...`) |
| 04-schema-types.md | 26 | classic/schemas.ts:115-121 | YES | YES | YES (exact match) |
| 04-schema-types.md | 38 | classic/schemas.ts:161-181 | YES | YES | YES (subset shown, rest omitted) |
| 04-schema-types.md | 55 | classic/schemas.ts:150-158 | YES | YES | YES (exact match) |
| 04-schema-types.md | 72 | classic/schemas.ts:33-67 | YES | YES | YES (simplified, `// ... deduplication`) |
| 04-schema-types.md | 106 | classic/schemas.ts:455-456 | YES | YES | YES (exact match) |
| 04-schema-types.md | 145 | classic/checks.ts:1-32 | YES | YES | YES (subset shown, `// ...`) |
| 04-schema-types.md | 178 | classic/errors.ts:9-23 | YES | YES | YES (exact match) |
| 04-schema-types.md | 189 | classic/errors.ts:65-67 | YES | YES | YES (exact match) |
| 04-schema-types.md | 200 | core/standard-schema.ts:34-47 | YES | YES | YES (exact match) |
| 05-innovation-summary.md | 10 | core/core.ts:68-74 | YES | YES | YES (exact match) |
| 05-innovation-summary.md | 32 | mini/external.ts:1-8 | YES | YES | YES |
| 05-innovation-summary.md | 37 | classic/external.ts:9-12 | YES | YES | YES (exact match) |
| 05-innovation-summary.md | 50 | core/parse.ts:30 | YES | YES | YES (exact match) |
| 05-innovation-summary.md | 54 | classic/parse.ts:8-9 | YES | YES | YES (exact match) |
| 05-innovation-summary.md | 67 | classic/schemas.ts:44-55 | YES | YES | YES (exact match, simplified) |
| 05-innovation-summary.md | 89 | core/checks.ts:20-26 | YES | YES | YES (exact match) |
| 05-innovation-summary.md | 101 | core/checks.ts:70-77 | YES | YES | YES (exact match) |
| 05-innovation-summary.md | 119 | core/parse.ts:103-106 | YES | YES | YES (exact match) |
| 05-innovation-summary.md | 133 | core/standard-schema.ts:96-106 | YES | YES | YES (exact match) |
| 06-micro-bundle.md | 42 | core/index.ts:1-16 | YES | YES | YES (subset shown, `...`) |
| 06-micro-bundle.md | 73 | mini/external.ts:1-7 | YES | YES | YES (simplified, comment added) |
| 06-micro-bundle.md | 98 | classic/external.ts:9-12 | YES | YES | YES (exact match) |
| 06-micro-bundle.md | 115 | package.json:36-47 | YES | YES | YES |

### ISSUE 1: $ZodArray code block simplified beyond source

**Doc**: 02-type-system.md line 175, citing `core/schemas.ts:1637-1678`

The walkthrough shows a simplified version of the `$ZodArray` constructor. The actual source at lines 1637-1678 includes additional detail:
- The actual source extracts `const item = input[i]` as a separate variable (line 1657)
- The actual source passes `{ value: item, issues: [] }` (not `{ value: input[i], issues: [] }` as the walkthrough implies)

However, the walkthrough uses `// Simplified from:` style is NOT used here -- it uses `// Source:` which implies exactness. The content is close but not an exact copy. This is a **minor accuracy issue** -- the semantics are preserved but the code is a paraphrase, not a quotation.

**Verdict**: PASS with 1 minor issue (paraphrased code block labeled as "Source" rather than "Simplified from").

---

## Check 2: Directory Structure

**Method**: Find all directory tree listings in the walkthrough. `ls` the actual directories. Verify every listed path exists.

### Core directory (01-overview.md line 70-79)

Walkthrough lists:
```
core/
  api.ts, checks.ts, config.ts, core.ts, doc.ts, errors.ts,
  index.ts, json-schema-generator.ts, json-schema-processors.ts,
  json-schema.ts, parse.ts, regexes.ts, registries.ts, schemas.ts,
  standard-schema.ts, tests/, to-json-schema.ts, util.ts,
  versions.ts, zsf.ts
```

Actual (`ls` of `packages/zod/src/v4/core/`):
```
api.ts  checks.ts  config.ts  core.ts  doc.ts  errors.ts  index.ts
json-schema-generator.ts  json-schema-processors.ts  json-schema.ts
parse.ts  regexes.ts  registries.ts  schemas.ts  standard-schema.ts
tests/  to-json-schema.ts  util.ts  versions.ts  zsf.ts
```

**Match**: PASS. All 19 entries (18 files + 1 directory) verified. The walkthrough says "19 source files" but `tests/` is a directory, so technically 18 source files + 1 test directory = 19 entries. The walkthrough's "19 source files" claim is slightly inaccurate since `tests/` is not a source file, but this is a minor phrasing issue.

### Classic directory (01-overview.md line 111-118)

Walkthrough lists:
```
classic/
  checks.ts, coerce.ts, compat.ts, errors.ts, external.ts,
  from-json-schema.ts, index.ts, iso.ts, parse.ts, schemas.ts,
  tests/
```

Actual (`ls` of `packages/zod/src/v4/classic/`):
```
checks.ts  coerce.ts  compat.ts  errors.ts  external.ts
from-json-schema.ts  index.ts  iso.ts  parse.ts  schemas.ts  tests
```

**Match**: PASS. All 11 entries (10 files + 1 directory) verified. Walkthrough says "11 source files" which has the same `tests/` quirk.

### Mini directory

Walkthrough (06-micro-bundle.md line 57) claims "8 source files" for mini.

Actual (`ls` of `packages/zod/src/v4/mini/`):
```
checks.ts  coerce.ts  external.ts  index.ts  iso.ts  parse.ts  schemas.ts  tests
```

That's 7 files + 1 tests directory = 8 entries. PASS.

**Verdict**: PASS

---

## Check 3: API Signatures

**Method**: Find all interface/type/function signatures shown in walkthrough. Search in source. Compare fields, parameters, types.

### $constructor (02-type-system.md line 10-16)

Walkthrough:
```ts
export function $constructor<T extends ZodTrait, D = T["_zod"]["def"]>(
  name: string,
  initializer: (inst: T, def: D) => void,
  params?: { Parent?: typeof Class }
): $constructor<T, D>
```

Source (core.ts:17-21): Exact match. PASS.

### $ZodType (02-type-system.md line 41-49)

Walkthrough:
```ts
export interface $ZodType<
  O = unknown, I = unknown,
  Internals extends $ZodTypeInternals<O, I> = $ZodTypeInternals<O, I>,
> {
  _zod: Internals;
  "~standard": $ZodStandardSchema<this>;
}
```

Source (schemas.ts:179-186): Exact match. PASS.

### $ZodTypeInternals (02-type-system.md line 55-62)

Walkdown:
```ts
export interface $ZodTypeInternals<out O = unknown, out I = unknown> extends _$ZodTypeInternals {
  output: O;
  input: I;
}
```

Source (schemas.ts:168-173): Exact match. PASS.

### _$ZodTypeInternals (02-type-system.md line 67-87)

Walkthrough lists fields: `version`, `def`, `deferred`, `run`, `parse`, `traits`, `optin`, `optout`, `values`, `propValues`, `pattern`, `constr`, `bag`, `isst`, `processJSONSchema`, `toJSONSchema`, `parent`.

Source (schemas.ts:96-166): All listed fields present. `processJSONSchema` simplified to `((...) => void)`. PASS.

### $ZodTypeDef.type (02-type-system.md line 94-107)

**Walkthrough claims**: "32 distinct type literals"

**Actual count**: Counting the type literals in the source (schemas.ts:50-94):
```
string, number, int, boolean, bigint, symbol,
null, undefined, void, never, any, unknown,
date, object, record, file, array, tuple,
union, intersection, map, set, enum, literal,
nullable, optional, nonoptional, success, transform,
default, prefault, catch, nan, pipe, readonly,
template_literal, promise, lazy, function, custom
```

**Actual count is 40, not 32.** This is a factual error.

The walkthrough text at line 109 states: "That is 32 distinct type literals, each corresponding to a specific schema constructor." The actual source has **40** type literals.

**Verdict**: FAIL -- type literal count is wrong (claimed 32, actual 40).

### ParsePayload (02-type-system.md line 205-211)

Walkthrough:
```ts
export interface ParsePayload<T = unknown> {
  value: T;
  issues: errors.$ZodRawIssue[];
  aborted?: boolean;
  fallback?: boolean | undefined;
}
```

Source (schemas.ts:34-44): Exact match. PASS.

### ParseContext (03-validation-engine.md line 131-139)

Walkthrough:
```ts
export interface ParseContext<T extends errors.$ZodIssueBase = never> {
  readonly error?: errors.$ZodErrorMap<T>;
  readonly reportInput?: boolean;
  readonly jitless?: boolean;
}
```

Source (schemas.ts:16-25): Exact match (comment lines omitted). PASS.

### ParseContextInternal (03-validation-engine.md line 145-151)

Walkthrough:
```ts
export interface ParseContextInternal<...> extends ParseContext<T> {
  readonly async?: boolean | undefined;
  readonly direction?: "forward" | "backward";
  readonly skipChecks?: boolean;
}
```

Source (schemas.ts:28-32): Exact match. PASS.

### ZodSafeParseResult (03-validation-engine.md line 59-62)

Source (classic/parse.ts:4-6): Exact match. PASS.

### ZodType (classic) (04-schema-types.md line 10-20)

Source (classic/schemas.ts:78-93): Match. Walkthrough uses `// ... plus parsing, encoding, refinement, and wrapper methods` to abbreviate. PASS.

### ZodType parsing methods (04-schema-types.md line 26-31)

Source (classic/schemas.ts:115-121): Exact match. PASS.

### ZodType wrapper methods (04-schema-types.md line 38-50)

Source (classic/schemas.ts:161-181): Subset shown. The walkthrough omits `exactOptional`, `nonoptional`, `prefault` and includes a subset. This is a simplification, acceptable. PASS.

### ZodType refinement methods (04-schema-types.md line 55-65)

Source (classic/schemas.ts:150-158): Exact match. PASS.

### ZodError (04-schema-types.md line 178-186)

Walkthrough:
```ts
export interface ZodError<T = unknown> extends $ZodError<T> {
  format(): core.$ZodFormattedError<T>;
  flatten(): core.$ZodFlattenedError<T>;
  addIssue(issue: core.$ZodIssue): void;
  addIssues(issues: core.$ZodIssue[]): void;
  isEmpty: boolean;
}
```

Source (classic/errors.ts:9-23): The source has additional overloads for `format` and `flatten` (with mapper parameter), plus deprecation annotations. The walkthrough shows the simplified version. PASS.

### ZodRealError (04-schema-types.md line 189-193)

Source (classic/errors.ts:65-67): Exact match. PASS.

### StandardSchemaV1 (04-schema-types.md line 200-213)

Source (standard-schema.ts:34-47): Exact match. PASS.

### $ZodCheckInternals (05-innovation-summary.md line 89-95)

Walkthrough:
```ts
export interface $ZodCheckInternals<T> {
  def: $ZodCheckDef;
  issc?: errors.$ZodIssueBase;
  check(payload: schemas.ParsePayload<T>): util.MaybeAsync<void>;
  onattach: ((schema: schemas.$ZodType) => void)[];
}
```

Source (core/checks.ts:20-26): Exact match. PASS.

### $ZodIssue (special focus)

The walkthrough does NOT explicitly list $ZodIssue fields. It references `$ZodIssue` as a union type in 04-schema-types.md (line 182: `addIssue(issue: core.$ZodIssue)`) and in the error handling section. The source defines `$ZodIssue` as a union of 11 issue subtypes at errors.ts:180-191. The walkthrough correctly describes the issue system without enumerating all subtypes.

**Verdict**: PARTIAL PASS -- one factual error on type literal count (40 vs claimed 32).

---

## Check 4: Version Number

**Walkthrough claim** (01-overview.md line 3): "Version: 4.4.3"

**Source** (`packages/zod/package.json` line 3): `"version": "4.4.3"`

**Source** (`packages/zod/src/v4/core/versions.ts` lines 1-5):
```ts
export const version = {
  major: 4,
  minor: 4,
  patch: 3 as number,
} as const;
```

The walkthrough correctly states the version as 4.4.3 and shows the version object (01-overview.md line 125-131) matching the source exactly.

**Verdict**: PASS

---

## Check 5: Architecture Claims

### Claim: "Core layer has no locale configured" (01-overview.md line 58, 05-innovation-summary.md line 37)

Verified: `core/index.ts` does not import or call any locale configuration. The `core/external.ts` does not exist -- there is no standalone entry point that configures locale for core. PASS.

### Claim: "Classic layer configures default English locale via config(en())" (01-overview.md line 96, 05-innovation-summary.md line 37)

Verified: `classic/external.ts` lines 9-11:
```ts
import { config } from "../core/index.js";
import en from "../locales/en.js";
config(en());
```
PASS.

### Claim: "Mini layer does not configure locale" (01-overview.md line 83, 05-innovation-summary.md line 32)

Verified: `mini/external.ts` has no locale import or config() call. PASS.

### Claim: "Core uses $ZodRealError, classic uses ZodRealError" (03-validation-engine.md line 157-176)

Verified: `core/parse.ts` line 30 uses `errors.$ZodRealError`. `classic/parse.ts` line 13 uses `ZodRealError` imported from `./errors.js`. PASS.

### Claim: "ZodRealError extends native Error" (04-schema-types.md line 189-193)

Verified: `classic/errors.ts` line 65-67:
```ts
export const ZodRealError: core.$constructor<ZodError> = core.$constructor("ZodError", initializer, {
  Parent: Error,
});
```
PASS.

### Claim: "Classic adds fluent builder methods" (04-schema-types.md passim)

Verified: The classic `ZodType` interface (classic/schemas.ts:78+) declares 20+ methods including optional, nullable, default, array, transform, pipe, refine, etc. PASS.

### Claim: "Mini provides no fluent method chaining" (06-micro-bundle.md line 66)

Verified: The mini `ZodMiniType` interface provides parse, safeParse, check, clone, brand, register but no optional/nullable/transform etc. PASS.

### Claim: "$constructor uses Symbol.hasInstance with trait-based identity" (02-type-system.md line 20)

Verified: core.ts:69-74 defines `Symbol.hasInstance` on the constructor that checks `_zod.traits.has(name)`. PASS.

### Claim: "Three-layer architecture: classic builds on mini builds on core" (01-overview.md line 46-54)

Verified: classic imports from core; mini imports from core. However, classic does NOT import from mini -- both classic and mini independently wrap core. The walkthrough's diagram shows:
```
   classic/
      |
   mini/
      |
   core/
```

This implies classic depends on mini, which is **incorrect**. Looking at the imports:
- `classic/external.ts` imports from `"../core/index.js"` -- NOT from mini
- `mini/external.ts` imports from `"../core/index.js"` -- from core

Classic and mini are **parallel** layers over core, not a stacked dependency chain. The diagram is misleading.

**Verdict**: FAIL on this claim. Classic does NOT build on mini; both are independent wrappers over core.

### Claim: "Lazy method binding keeps per-instance memory low" (04-schema-types.md line 69-94)

Verified: `classic/schemas.ts:33-67` defines `_installLazyMethods` which uses prototype getters with lazy binding. PASS.

### Claim: "onattach callbacks modify schema metadata at construction" (02-type-system.md line 138)

Verified: `core/schemas.ts:204-208` iterates checks and calls `ch._zod.onattach`. `core/checks.ts:70-77` shows `$ZodCheckLessThan` pushing to `bag.maximum` via onattach. PASS.

### Claim: "Encode/decode provide bidirectional codecs" (03-validation-engine.md line 86-98)

Verified: `core/parse.ts:103-106` shows `_encode` sets `direction: "backward"`. `_decode` at lines 116-118 simply calls `_parse`. PASS.

### Claim: Package exports (01-overview.md line 35-42, 06-micro-bundle.md line 115-122)

Walkthrough lists:
```
"."          -> ./src/index.ts        (full classic API)
"./mini"     -> ./src/mini/index.ts   (minimal bundle)
"./v4"       -> ./src/v4/index.ts     (v4 classic re-export)
"./v4/core"  -> ./src/v4/core/index.ts (core primitives only)
"./v4/mini"  -> ./src/v4/mini/index.ts (v4 minimal)
```

Source `package.json` zshy.exports (lines 35-47):
```
".": "./src/index.ts"
"./mini": "./src/mini/index.ts"
"./locales": "./src/locales/index.ts"
"./v3": "./src/v3/index.ts"
"./v4": "./src/v4/index.ts"
"./v4-mini": "./src/v4-mini/index.ts"
"./v4/mini": "./src/v4/mini/index.ts"
"./v4/core": "./src/v4/core/index.ts"
"./v4/locales": "./src/v4/locales/index.ts"
"./v4/locales/*": "./src/v4/locales/*"
```

The walkthrough omits `./locales`, `./v3`, `./v4-mini`, `./v4/locales`, and `./v4/locales/*`. This is a simplification (the walkthrough focuses on the v4 layers). PASS as a deliberate simplification, but noted for completeness.

**Verdict**: PARTIAL PASS -- one significant architecture error (classic does NOT depend on mini).

---

## Summary

| Check | Result | Notes |
|-------|--------|-------|
| 1. Code Example Existence | PASS (1 minor) | 49 code blocks verified. 1 code block ($ZodArray) is paraphrased but labeled as "Source" instead of "Simplified from". |
| 2. Directory Structure | PASS | All listed paths verified. Core=19 entries, Classic=11 entries, Mini=8 entries. |
| 3. API Signatures | PARTIAL PASS | $ZodTypeDef.type literal count is 40, not 32 as claimed. All other signatures match. |
| 4. Version Number | PASS | 4.4.3 matches package.json and versions.ts exactly. |
| 5. Architecture Claims | PARTIAL PASS | Classic does NOT build on top of mini -- they are parallel layers over core. The diagram implying classic -> mini -> core is misleading. |

## Overall: PARTIAL PASS

## Issues Requiring Fixes

1. **[MEDIUM] Type literal count wrong**: 02-type-system.md line 109 claims "32 distinct type literals" but the actual source has **40**. Fix the number, or if the walkthrough was generated from an earlier version, verify the source hasn't changed.

2. **[MEDIUM] Architecture diagram is misleading**: 01-overview.md lines 48-54 and 05-innovation-summary.md lines 23-28 show a stacked diagram `classic -> mini -> core`, implying classic depends on mini. In reality, classic and mini are **parallel** wrappers over core. The diagram should show classic and mini as siblings, not parent-child. 06-micro-bundle.md line 7-24 has the same issue.

3. **[LOW] $ZodArray code block paraphrased**: 02-type-system.md line 175 uses `// Source:` but the code is a paraphrase of the actual source, not an exact quote. Should either use `// Simplified from:` or show the exact source.

## Issues Not Requiring Fixes (noted for awareness)

- Walkthrough omits several package.json export entries (`./locales`, `./v3`, `./v4-mini`, `./v4/locales/*`). This is a reasonable simplification for a v4-focused walkthrough.
- `tests/` is counted as a "source file" in the directory descriptions. Minor phrasing issue.
- Several code blocks use `// ...` to indicate truncation. This is an accepted convention.
