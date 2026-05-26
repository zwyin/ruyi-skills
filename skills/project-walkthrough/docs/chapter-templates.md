# Chapter Templates

Starting point for planning chapters. Adapt to each project's specifics.

## AI Tool Template

For projects that are AI coding assistants, prompt engineering tools, AI agents, or AI workflow engines.

### Brief (7-8 chapters)

| # | Chapter | Source files to read |
|---|---------|---------------------|
| 1 | Overview — what it does, tech stack, key numbers | README, package.json |
| 2 | Architecture — component diagram, data flow | ARCHITECTURE.md or main source files |
| 3 | Core mechanism — the main innovation | Entry skill / core module |
| 4 | Skill/plugin system — how capabilities are organized | Skills directory, manifest |
| 5 | Key technical highlights — 3-5 innovations | Core source files |
| 6 | Comparison with alternatives | README alternatives section, industry knowledge |
| 7 | Innovation summary + impact | Synthesized from above |

### Medium (12-15 chapters, extends Brief)

All Brief chapters (expanded), plus:

| # | Additional Chapter | Source files to read |
|---|-------------------|---------------------|
| 8 | Hook/event system | Hook scripts, event handlers |
| 9 | Prompt engineering deep dive | Key skill files, prompt templates |
| 10 | Multi-model / cross-review (if applicable) | Review-related source |
| 11 | Security model | Security-related source, safety checks |
| 12 | Cross-platform support | Platform adapters, tool mappings |
| 13 | Developer workflow & testing | Test files, CI config |
| 14 | Design philosophy / ethos | ETHOS.md, CONTRIBUTING.md, code comments |

### Deep (15-20 chapters, extends Medium)

All Medium chapters (expanded), plus:

| # | Additional Chapter | Source files to read |
|---|-------------------|---------------------|
| 15 | Design evolution — version history | Git history, CHANGELOG, code comments |
| 16 | Line-by-line analysis of core algorithm | Core module (full read) |
| 17 | Complete security model with attack scenarios | Security source, threat analysis |
| 18 | Error handling & edge cases | Error handling code, fallback logic |
| 19 | Build your own — reimplementation guide | Synthesized from understanding |
| 20 | Industry impact & predictions | Synthesized from analysis |

---

## Library Template

For projects that are reusable libraries, frameworks, or SDKs.

### Brief (7-8 chapters)

| # | Chapter | Source files to read |
|---|---------|---------------------|
| 1 | Overview — what problem it solves, API surface | README, src/index.ts |
| 2 | Architecture — module structure, public vs internal | Directory structure, exports |
| 3 | Core API walkthrough | Main source files |
| 4 | Configuration & customization | Config files, options types |
| 5 | Key technical highlights | Core algorithm source |
| 6 | Comparison with alternatives | README, npm/registry comparison |
| 7 | Getting started + recommended patterns | README, examples |

### Medium (12-15 chapters)

All Brief chapters (expanded), plus:

| # | Additional Chapter |
|---|-------------------|
| 8 | Type system design (if TypeScript) |
| 9 | Plugin/extension API |
| 10 | Error handling strategy |
| 11 | Performance characteristics |
| 12 | Testing strategy |
| 13 | Migration & backwards compatibility |
| 14 | Internal implementation details for key features |

### Deep (15-20 chapters)

All Medium chapters (expanded), plus:

| # | Additional Chapter |
|---|-------------------|
| 15 | Design evolution — API changes over versions |
| 16 | Line-by-line analysis of core algorithm |
| 17 | Edge cases & corner cases |
| 18 | Bundle size & tree-shaking analysis |
| 19 | Build your own — minimal reimplementation |
| 20 | Contribution guide & community patterns |

---

## Web App Template

For projects that are web applications, SaaS products, or full-stack projects.

### Brief (7-8 chapters)

| # | Chapter | Source files to read |
|---|---------|---------------------|
| 1 | Overview — what it does, tech stack, users | README, package.json |
| 2 | Architecture — frontend/backend split, services | Directory structure |
| 3 | Data model — database schema, key entities | Migrations, schema files |
| 4 | API surface — endpoints, auth model | Routes, controllers |
| 5 | Key technical highlights | Core feature source |
| 6 | Deployment & infrastructure | Docker, CI config, deploy scripts |
| 7 | Comparison with similar apps | Synthesized |

### Medium (12-15 chapters)

All Brief chapters (expanded), plus:

| # | Additional Chapter |
|---|-------------------|
| 8 | Authentication & authorization flow |
| 9 | State management (frontend) |
| 10 | Database access patterns |
| 11 | Caching strategy |
| 12 | Error handling & monitoring |
| 13 | Testing strategy |
| 14 | CI/CD pipeline |

### Deep (15-20 chapters)

All Medium chapters (expanded), plus:

| # | Additional Chapter |
|---|-------------------|
| 15 | Design evolution — feature history |
| 16 | Line-by-line analysis of core feature |
| 17 | Security model — threat analysis |
| 18 | Performance optimization techniques |
| 19 | Build your own — minimal version |
| 20 | Scaling considerations & bottlenecks |

---

## CLI Tool Template

For projects that are command-line tools, build tools, or developer utilities.

### Brief (7-8 chapters)

| # | Chapter | Source files to read |
|---|---------|---------------------|
| 1 | Overview — what it does, installation, usage | README, package.json |
| 2 | Architecture — command structure, plugin system | Directory structure, bin/ |
| 3 | Command handling — how commands are parsed and executed | CLI entry point |
| 4 | Configuration system | Config files, options parsing |
| 5 | Key technical highlights | Core module |
| 6 | Comparison with alternatives | Synthesized |
| 7 | Extensibility — plugins, hooks | Plugin directory, hook system |

### Medium (12-15 chapters)

All Brief chapters (expanded), plus:

| # | Additional Chapter |
|---|-------------------|
| 8 | Output formatting & user experience |
| 9 | File system operations |
| 10 | Error handling & exit codes |
| 11 | Testing strategy |
| 12 | Cross-platform support |
| 13 | Performance — startup time, memory |
| 14 | Distribution & packaging |

### Deep (15-20 chapters)

All Medium chapters (expanded), plus:

| # | Additional Chapter |
|---|-------------------|
| 15 | Design evolution — command history |
| 16 | Line-by-line analysis of core command |
| 17 | Security model — input validation, sandboxing |
| 18 | Edge cases — unusual inputs, large files |
| 19 | Build your own — minimal CLI tool |
| 20 | Internal APIs — for plugin authors |

---

## Document/Report Template

For research papers, playbooks, study guides, and other non-code document collections.

### Key Principle: 1:1 Chapter Preservation

Default strategy is to preserve every input chapter as a separate output chapter. Do NOT consolidate unless the user explicitly selected `focused` or `overview` scope in the confirmation gate.

### Full Scope (= input chapter count)

| # | Chapter | Content source |
|---|---------|---------------|
| 1 | Overview — document context, authors, purpose, key numbers | Front matter, foreword, introduction |
| 2-N | One chapter per input chapter | Each corresponding input chapter |
| N+1 | Cross-cutting analysis — patterns across chapters (if applicable) | Synthesized from all chapters |
| N+2 | Practical takeaways / action guide (if applicable) | Synthesized from findings |
| N+3 | Critical assessment — strengths, limitations, gaps | Synthesized analysis |

Each output chapter should:
- Preserve the original chapter's key data, statistics, and findings
- Include direct quotes as blockquotes with source attribution
- Preserve data tables (do not summarize into fewer rows)
- Add cross-references to related chapters
- Add audience-appropriate explanation (general: analogies; dev: direct)

### Focused Scope (select key chapters)

When user selects focused scope:
1. Identify 8-10 most impactful chapters based on: data density, novelty, practical value
2. Give these chapters full detailed treatment
3. Create one "Additional Findings" chapter summarizing the remaining chapters (2-5 sentences each)

### Overview Scope (thematic consolidation)

When user selects overview scope:
1. Group input chapters into 5-8 thematic clusters
2. Each thematic chapter covers 2-4 original chapters
3. Focus on key findings and connections between chapters

### Chapter depth levels for documents

| Depth | What each chapter contains |
|-------|---------------------------|
| **detailed** | Full content coverage + preserved data tables + direct quotes + cross-references + quiz questions (3-5) + critical notes |
| **standard** | Key findings + important data tables (top rows) + selected quotes + cross-references + quiz (1-2) |
| **summary** | Core finding (2-5 sentences) + key metric or statistic + no quiz |

### Quiz design for documents

Unlike software projects where quiz tests code understanding, document quizzes test **content comprehension**:

- **Fact-based**: "What percentage of challenges were invisible costs?" (answer: 77%)
- **Application**: "If your project has X characteristic, which finding applies?"
- **Analysis**: "Which two findings seem contradictory? How does the report resolve this?"
- **Evaluation**: "Does the report's methodology support this conclusion? Why or why not?"

---

## Game Engine Template

For projects that are game engines, rendering frameworks, or real-time interactive systems.

### Brief (7-8 chapters)

| # | Chapter | Source files to read |
|---|---------|---------------------|
| 1 | Overview — what it does, supported platforms, key numbers | README, CMakeLists/Makefile, package.json |
| 2 | Architecture — subsystem diagram (render, physics, audio, script) | Engine directory structure, main loop |
| 3 | Rendering pipeline — draw calls, shaders, materials | Renderer source, shader files |
| 4 | Scene management — entity/component hierarchy | Scene graph, ECS source |
| 5 | Scripting / gameplay API | Script bindings, API surface |
| 6 | Key technical highlights — 3-5 innovations | Core subsystem source |
| 7 | Comparison with alternatives (Unity, Unreal, Godot) | README, industry knowledge |

### Medium (12-15 chapters)

All Brief chapters (expanded), plus:

| # | Additional Chapter | Source files to read |
|---|-------------------|---------------------|
| 8 | ECS architecture — entity, component, system design | ECS directory, component definitions |
| 9 | Asset pipeline — import, serialization, hot-reload | Asset manager, resource loaders |
| 10 | Physics integration — collision, rigid body, constraints | Physics module source |
| 11 | Input handling — gamepad, keyboard, mouse, touch | Input manager source |
| 12 | Audio system — spatial audio, mixing | Audio module source |
| 13 | Windowing & platform abstraction | Platform layer, window manager |
| 14 | Build system & cross-compilation | Build scripts, CI config |

### Deep (15-20 chapters)

All Medium chapters (expanded), plus:

| # | Additional Chapter |
|---|-------------------|
| 15 | Design evolution — engine history, API changes |
| 16 | Line-by-line analysis of main loop / frame pipeline |
| 17 | Memory management — allocators, pools, GPU buffers |
| 18 | Multithreading — job system, parallel rendering |
| 19 | Performance profiling — frame time budget, bottlenecks |
| 20 | Build your own — minimal game engine reimplementation |

---

## Database / Storage Engine Template

For projects that are databases, storage engines, key-value stores, or data pipelines.

### Brief (7-8 chapters)

| # | Chapter | Source files to read |
|---|---------|---------------------|
| 1 | Overview — what it stores, query model, key numbers | README, Cargo.toml / go.mod |
| 2 | Architecture — storage engine, query path, replication | Directory structure, ARCHITECTURE.md |
| 3 | Storage model — on-disk format, page/segment layout | Storage engine source |
| 4 | Query processing — parse, plan, execute | Query engine source |
| 5 | Indexing — B-tree, LSM, hash, or custom | Index source files |
| 6 | Key technical highlights | Core algorithm source |
| 7 | Comparison with alternatives (MySQL, Postgres, RocksDB, etc.) | README, benchmarks |

### Medium (12-15 chapters)

All Brief chapters (expanded), plus:

| # | Additional Chapter | Source files to read |
|---|-------------------|---------------------|
| 8 | Transaction model — ACID guarantees, isolation levels | Transaction manager source |
| 9 | Write-ahead log (WAL) & recovery | WAL source, recovery module |
| 10 | Compaction / garbage collection | Compaction source, GC logic |
| 11 | Replication & consensus | Replication source, consensus protocol |
| 12 | Caching — buffer pool, page cache | Cache manager source |
| 13 | Schema / type system | Schema definitions, type registry |
| 14 | Client protocol & API | Server entry, protocol handlers |

### Deep (15-20 chapters)

All Medium chapters (expanded), plus:

| # | Additional Chapter |
|---|-------------------|
| 15 | Design evolution — format changes, version history |
| 16 | Line-by-line analysis of read/write path |
| 17 | Concurrency control — lock manager, MVCC |
| 18 | Edge cases — crash recovery, partial writes, corruption |
| 19 | Performance — benchmark methodology, tuning knobs |
| 20 | Build your own — minimal storage engine |

---

## Compiler / Interpreter Template

For projects that are compilers, interpreters, transpilers, or language runtimes.

### Brief (7-8 chapters)

| # | Chapter | Source files to read |
|---|---------|---------------------|
| 1 | Overview — language features, target platforms, key numbers | README, Cargo.toml / build config |
| 2 | Architecture — compilation pipeline diagram | Compiler directory structure |
| 3 | Lexer & parser — tokenization, grammar, AST | Lexer/parser source |
| 4 | Type system — type checking, inference | Type checker source |
| 5 | Code generation — IR, target output | Codegen source |
| 6 | Key technical highlights | Core pass source |
| 7 | Comparison with alternatives (LLVM, GCC, V8, etc.) | README, benchmarks |

### Medium (12-15 chapters)

All Brief chapters (expanded), plus:

| # | Additional Chapter | Source files to read |
|---|-------------------|---------------------|
| 8 | AST design — node types, visitor pattern | AST definitions, visitor source |
| 9 | Semantic analysis — name resolution, scope | Semantic analysis source |
| 10 | Optimization passes — dead code, inlining, constant folding | Optimization pass source |
| 11 | Error reporting — diagnostics, suggestions, recovery | Error types, reporter source |
| 12 | Standard library / builtins | Stdlib source, builtin definitions |
| 13 | Build system & bootstrap | Build scripts, bootstrap process |
| 14 | Testing strategy — snapshot tests, fuzzing | Test directory, fuzz targets |

### Deep (15-20 chapters)

All Medium chapters (expanded), plus:

| # | Additional Chapter |
|---|-------------------|
| 15 | Design evolution — language changes, AST migrations |
| 16 | Line-by-line analysis of core compilation pass |
| 17 | Garbage collection / memory model (if runtime) |
| 18 | Edge cases — ambiguous grammar, type edge cases, platform quirks |
| 19 | Performance — compile-time benchmarks, memory usage |
| 20 | Build your own — minimal compiler/interpreter |

---

## Adapting Templates

These templates are starting points. When adapting:

1. **Remove irrelevant chapters.** If the project has no security model, don't force one.
2. **Add unique chapters.** If the project does something unusual (e.g. browser automation, ML inference), add a dedicated chapter.
3. **Merge overlapping chapters.** If two template chapters cover the same ground in a specific project, merge them.
4. **Respect the project's own organization.** If the project has a clear module structure, mirror it in chapters.

### What makes a good chapter

- **One clear topic** — not "Miscellaneous features"
- **Source-backed** — you can point to specific files that inform this chapter
- **Stand-alone readable** — makes sense without reading other chapters
- **Non-trivial** — not just "this file has 200 lines of code"

### Source citation rules (all depth levels)

Every code block must have a `<!-- Simplified from: -->` comment. This applies to all depth levels including deep chapters like "Build your own" and "Line-by-line analysis":

- All code blocks ≥20 chars: `<!-- Simplified from: path/to/file.ext:lines -->`
- Never use `// Source:` — always `Simplified from:` since walkthrough code is always simplified
- For "Build your own" chapters: cite the original source file being reimplemented
- For "Line-by-line analysis" chapters: cite the exact file and line range being analyzed
