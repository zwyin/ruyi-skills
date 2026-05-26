# bat Walkthrough Accuracy Verification Report

- Walkthrough: `examples/bat/docs/` (5 chapters)
- Source: `examples/_src_bat/` (tag v0.26.1)
- Date: 2026-05-07
- Verifier: Independent accuracy audit (automated)

---

## Check 1: Code Example Existence and Source Citation

**Verdict: FAIL**

### 1.1 Source Citation Status

Searched all 5 walkthrough md files for `// Source:` and `// Simplified from:` patterns. **Zero source citations found.** Every code block in the walkthrough lacks a source citation.

All 16 code blocks across the 5 files are marked **NO_CITATION**:

| File | Lines | Language | Citation | Issue |
|------|-------|----------|----------|-------|
| 01-overview.md | 17-22 | bash | NO_CITATION | Usage example, no source needed |
| 01-overview.md | 28-42 | tree | NO_CITATION | Directory structure, verifiable |
| 01-overview.md | 58-69 | text | NO_CITATION | Architecture diagram, no source |
| 02-input-and-config.md | 23-27 | text | NO_CITATION | Config priority, no source |
| 02-input-and-config.md | 32-37 | config | NO_CITATION | Config file example, no source |
| 02-input-and-config.md | 44-50 | bash | NO_CITATION | CLI usage, no source needed |
| 03-syntax-highlighting.md | 7-19 | text | NO_CITATION | Flow diagram, no source |
| 03-syntax-highlighting.md | 24-32 | text | NO_CITATION | Language detection chain, no source |
| 03-syntax-highlighting.md | 40-47 | **rust** | NO_CITATION | **CRITICAL: fabricated code** |
| 03-syntax-highlighting.md | 58-61 | bash | NO_CITATION | CLI usage, no source needed |
| 04-git-and-paging.md | 9-12 | bash | NO_CITATION | CLI usage, no source needed |
| 04-git-and-paging.md | 15-20 | text | NO_CITATION | Output example, illustrative |
| 04-git-and-paging.md | 24-29 | text | NO_CITATION | Detection strategy, no source |
| 04-git-and-paging.md | 45-51 | text | NO_CITATION | Paging decision logic, no source |
| 04-git-and-paging.md | 55-62 | text | NO_CITATION | Pager selection chain, no source |
| 05-innovation-summary.md | 48-51 | bash | NO_CITATION | Alias suggestion, no source |

### 1.2 Code Example Accuracy (Rust block at 03-syntax-highlighting.md:40-47)

The walkthrough presents:

```rust
// 1. Built-in mode: compiled into binary
let syntax_set = SyntaxSet::load_defaults_newlines();

// 2. Cache mode: loaded from cache directory
let syntax_set = asset::get_syntax_set()?;
```

**Neither line of code exists in the source.** Specifically:

- `SyntaxSet::load_defaults_newlines()` -- searched all source files, zero matches. The source uses `SerializedSyntaxSet::FromBinary(...)` and `SerializedSyntaxSet::FromFile(...)` patterns instead, with lazy deserialization via `OnceCell`.
- `asset::get_syntax_set()` -- the actual API is `HighlightingAssets::get_syntax_set(&self) -> Result<&SyntaxSet>`, a method on the `HighlightingAssets` struct, not a free function on an `asset` module.

This is a **fabricated code example** that does not correspond to any source code. The conceptual intent (two loading modes) is correct, but the code is invented.

---

## Check 2: Directory Structure Accuracy

**Verdict: PARTIAL PASS**

Walkthrough (01-overview.md:28-42) presents this structure:

```
bat/
  src/
    bin/bat/main.rs        -- CLI entry
    lib.rs                 -- Library API
    controller.rs          -- Main control flow
    input.rs               -- Input handling
    printer.rs             -- Syntax highlight engine
    output.rs              -- Output & paging
    config.rs              -- Configuration management
    assets/                -- Syntax & theme resources
    syntax_mapping/        -- Language mapping rules
  tests/                   -- Integration tests
  assets/                  -- Bundled resources
  Cargo.toml              -- Rust project config
```

### Verification results:

| Path | Exists | Notes |
|------|--------|-------|
| `src/bin/bat/main.rs` | YES | Confirmed |
| `src/lib.rs` | YES | Confirmed |
| `src/controller.rs` | YES | Confirmed |
| `src/input.rs` | YES | Confirmed |
| `src/printer.rs` | YES | Confirmed |
| `src/output.rs` | YES | Confirmed |
| `src/config.rs` | YES | Confirmed |
| `src/assets/` | YES | Confirmed (contains assets_metadata.rs, build_assets/, etc.) |
| `src/syntax_mapping/` | YES | Confirmed (contains builtin.rs, builtins/, ignored_suffixes.rs) |
| `tests/` | YES | Confirmed |
| `assets/` | YES | Confirmed (syntaxes.bin, themes.bin, etc.) |
| `Cargo.toml` | YES | Confirmed |

**Omissions (not incorrect, but incomplete):** The actual `src/` contains 28 files/dirs, while the walkthrough shows only 8. Omitted significant files include: `diff.rs`, `pager.rs`, `paging.rs`, `less.rs`, `lessopen.rs`, `preprocessor.rs`, `pretty_printer.rs`, `style.rs`, `theme.rs`, `vscreen.rs`, `decorations.rs`, `error.rs`, `line_range.rs`, `wrapping.rs`, `terminal.rs`, `macros.rs`, `nonprintable_notation.rs`, `syntax_mapping.rs`. The walkthrough also omits `src/bin/bat/` sub-files: `app.rs`, `clap_app.rs`, `completions.rs`, `config.rs`, `directories.rs`, `assets.rs`.

**Verdict:** All listed paths exist. The structure is correct as a simplified overview. Marking PARTIAL PASS due to significant omissions but no false paths.

---

## Check 3: API Signature Verification

**Verdict: FAIL**

### 3.1 `SyntaxSet::load_defaults_newlines()`

- Walkthrough shows: `SyntaxSet::load_defaults_newlines()` as a free-standing call
- Source reality: This function does **not exist** anywhere in the bat source. It is a syntect API, but bat never calls it directly. bat uses `SerializedSyntaxSet` with lazy deserialization via `OnceCell`.

### 3.2 `asset::get_syntax_set()`

- Walkthrough shows: `asset::get_syntax_set()?` as a free function
- Source reality: The actual function is `HighlightingAssets::get_syntax_set(&self) -> Result<&SyntaxSet>` (assets.rs:92), a method on the `HighlightingAssets` struct, not a module-level function.

### 3.3 `Controller` struct

- Walkthrough implies: Controller orchestrates Input -> Config -> Controller -> Printer -> Output
- Source reality: `Controller` struct (controller.rs:22) has fields `config: &'a Config` and `assets: &'a HighlightingAssets`. Its `run()` method signature is `run(&self, inputs: Vec<Input>, output_handle: Option<&mut OutputHandle<'_>>) -> Result<bool>`. The walkthrough's high-level description is **conceptually correct**.

### 3.4 `PagingMode` enum

- Walkthrough (04-git-and-paging.md:35-41) implies: PagingMode with variants Always, QuitIfOneScreen, Never
- Source reality (paging.rs:1-7): `PagingMode { Always, QuitIfOneScreen, Never }` -- **exact match**.

### 3.5 `OutputType::from_mode`

- Walkthrough implies: from_mode decides paging based on mode
- Source reality (output.rs:76-89): `from_mode(paging_mode: PagingMode, wrapping_mode: WrappingMode, pager: Option<&str>) -> Result<Self>` -- the walkthrough omits `wrapping_mode` and `pager` parameters, and the actual auto-mode logic is more nuanced than described.

### 3.6 `get_git_diff`

- Walkthrough implies: get_git_diff compares working tree to HEAD
- Source reality (diff.rs:19): `get_git_diff(filename: &Path) -> Option<LineChanges>` uses `repo.diff_index_to_workdir()` -- **matches** the description.

**Summary:** 2 of 5 API checks have inaccuracies (fabricated Rust code block, wrong module path for get_syntax_set).

---

## Check 4: Version Number Verification

**Verdict: FAIL**

| Claim in Walkthrough | Actual in Source | Match? |
|---|---|---|
| `0.25.x` (01-overview.md:3) | `0.26.1` (Cargo.toml:9) | **NO** |
| `Rust 1.88+` (01-overview.md:48) | `rust-version = "1.88"` (Cargo.toml:14) | YES (MSRV is 1.88) |
| `syntect` (01-overview.md:49) | `syntect = "5.3.0"` (Cargo.toml:85) | YES |
| `clap` (01-overview.md:50) | `clap = "4.6.1"` (Cargo.toml:90) | YES |
| `git2` (01-overview.md:51) | `git2 = "0.20"` (Cargo.toml:80), optional with `git` feature | YES |
| `minus` (01-overview.md:52) | `minus = "5.6"` (Cargo.toml:55), optional with `paging` feature | YES |
| `nu-ansi-term` (01-overview.md:53) | `nu-ansi-term = "0.50.3"` (Cargo.toml:45) | YES |

**Critical issue:** The walkthrough states version `0.25.x` but the source is `0.26.1`. The sources-manifest.json also notes this as a stale claim. The `sources-manifest.json` commit_or_tag field correctly says `v0.26.1`, contradicting the walkthrough text.

---

## Check 5: Architecture Claim Verification

**Verdict: PARTIAL PASS**

### 5.1 Module responsibility claims

| Claim | Source Evidence | Verified? |
|---|---|---|
| `input.rs` handles input (file/stdin) | input.rs defines `Input`, `InputReader`, `InputKind` (OrdinaryFile, StdIn, CustomReader) | YES |
| `config.rs` manages configuration | config.rs defines `Config` struct with all style/paging/theme fields | YES |
| `controller.rs` orchestrates pipeline | controller.rs defines `Controller::run()` that calls input.open(), printer, output | YES |
| `printer.rs` is syntax highlight engine | printer.rs (36KB, largest file) defines `InteractivePrinter` and `SimplePrinter` | YES |
| `output.rs` handles output & paging | output.rs defines `OutputType` (Pager/BuiltinPager/Stdout) and paging logic | YES |
| `assets/` handles syntax & theme loading | assets.rs defines `HighlightingAssets` with `get_syntax_set()`, theme methods | YES |
| `syntax_mapping/` contains language mapping | syntax_mapping/ has builtin.rs, builtins/, ignored_suffixes.rs | YES |

### 5.2 Library usage claims

| Claim | Source Evidence | Verified? |
|---|---|---|
| Uses syntect for syntax highlighting | Cargo.toml: syntect 5.3.0; assets.rs imports `syntect::parsing::SyntaxSet` | YES |
| Uses clap for CLI parsing | Cargo.toml: clap 4.6.1 (optional, in minimal-application feature) | YES |
| Uses git2 for Git integration | Cargo.toml: git2 0.20 (optional, behind `git` feature); diff.rs imports `git2::{DiffOptions, Repository}` | YES |
| Uses minus for builtin pager | Cargo.toml: minus 5.6 (optional, behind `paging` feature); output.rs uses `minus::Pager`, `minus::dynamic_paging` | YES |
| Uses nu-ansi-term for ANSI colors | Cargo.toml: nu-ansi-term 0.50.3 | YES |

### 5.3 Behavioral claims

| Claim | Source Evidence | Verified? |
|---|---|---|
| Config priority: CLI > env > config file | main.rs:325-334 lists BAT_CONFIG_PATH, BAT_PAGER, BAT_STYLE, BAT_THEME env vars; clap_app.rs handles CLI args | PARTIALLY -- env vars confirmed, but the exact 3-tier merge priority is implemented in bin/bat/app.rs config loading, not in library config.rs |
| Encoding detection: try UTF-8 first, lossless fallback | input.rs uses `content_inspector` crate for content type detection (UTF-16LE/BE handling), NOT `encoding_rs` as implied. No "lossless conversion" is explicitly coded | PARTIALLY -- encoding detection exists but implementation differs |
| `--style full` = header + grid + numbers + changes + snip | style.rs: Full = Changes + Grid + HeaderFilename + HeaderFilesize + LineNumbers + Snip | **NO** -- walkthrough omits `HeaderFilesize`. Also `header` maps to `HeaderFilename` internally, not a monolithic "header" |
| `highlight` is a style component | Not present in source. The source has no `highlight` component | **NO** -- walkthrough (02-input-and-config.md:46) lists `highlight` as a style component, but the source enum has no such variant |

### 5.4 Pager selection chain

Walkthrough (04-git-and-paging.md:55-62) claims:
1. Built-in pager (minus)
2. BAT_PAGER env var
3. PAGER env var
4. less (default)

Source (pager.rs:100-109): The actual priority is:
1. `config_pager` (from --pager CLI or config file)
2. `BAT_PAGER` env var
3. `PAGER` env var
4. `"less"` (default)

The walkthrough **omits the CLI/config-file pager source** and incorrectly describes the priority chain. The built-in pager is triggered when `PagerKind::Builtin` is detected (output.rs:113), not as a separate priority level.

---

## Summary

| Check | Verdict | Key Issues |
|---|---|---|
| 1. Code example existence | **FAIL** | 0/16 code blocks have source citations; 1 Rust code block is fabricated |
| 2. Directory structure | **PARTIAL PASS** | All listed paths exist; significant omissions but no false paths |
| 3. API signatures | **FAIL** | 2/5 checks inaccurate: `SyntaxSet::load_defaults_newlines()` nonexistent; `asset::get_syntax_set()` wrong module path |
| 4. Version numbers | **FAIL** | Version stated as 0.25.x, actual is 0.26.1 |
| 5. Architecture claims | **PARTIAL PASS** | 5/7 behavioral claims verified; 2 inaccurate (`highlight` component nonexistent; `--style full` omits HeaderFilesize); pager priority chain is wrong |

---

## Overall: FAIL

The walkthrough has 2 outright FAILs and 2 PARTIAL PASSes out of 5 checks. Critical issues:

1. **Fabricated code** (03-syntax-highlighting.md:40-47): The Rust code block does not correspond to any source code. `SyntaxSet::load_defaults_newlines()` is never called in bat.
2. **Wrong version** (01-overview.md:3): States 0.25.x, source is 0.26.1.
3. **Nonexistent style component** (02-input-and-config.md:46): `highlight` is not a valid bat style component.
4. **Incomplete `--style full` description** (02-input-and-config.md:50): Omits `header-filesize` component.
5. **Zero source citations**: No code block links back to source file/line numbers.
6. **Pager priority chain** (04-git-and-paging.md:55-62): Omits CLI/config-file source; misrepresents built-in pager as a priority level.

### Recommended fixes:

- [ ] Update version from `0.25.x` to `0.26.1` in 01-overview.md:3
- [ ] Replace fabricated Rust code in 03-syntax-highlighting.md:40-47 with actual source (use `HighlightingAssets::from_binary()` / `from_cache()` patterns from assets.rs)
- [ ] Remove `highlight` from style component table in 02-input-and-config.md:46
- [ ] Add `header-filesize` to `--style full` description in 02-input-and-config.md:50
- [ ] Correct pager priority chain in 04-git-and-paging.md:55-62 to include CLI/config-file source
- [ ] Add source citations to all code blocks that reference source code
