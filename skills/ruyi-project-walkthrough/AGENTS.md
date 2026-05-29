# Project Walkthrough Generator

Generate a structured technical walkthrough of any software project — codebase, research report, or document collection. Outputs numbered markdown chapters + self-contained interactive HTML with dark/light mode, sidebar navigation, and quiz.

## Quick Start

Ask your AI assistant to run:

```
/project-walkthrough
```

Or with options:

```
/project-walkthrough /path/to/project --depth deep --audience dev --lang en
```

## Options

| Flag | Values | Default | Description |
|------|--------|---------|-------------|
| `[path]` | directory | `.` | Project to analyze |
| `--depth` | `brief`, `medium`, `deep`, `all` | `brief` | Analysis depth |
| `--audience` | `general`, `dev` | `general` | `general` adds analogies; `dev` is technical |
| `--lang` | `zh`, `zh-pure`, `en`, `bilingual` | `zh` | Output language |
| `--no-confirm` | (flag) | off | Skip confirmation, use defaults |
| `--version` | (flag) | off | Print version and exit |

## Platform Install

| Platform | Install |
|----------|---------|
| **Claude Code** | `/plugin marketplace add zwyin/project-walkthrough-skill` |
| **Cursor** | Copy `cursor/project-walkthrough.mdc` → `.cursor/rules/` |
| **Windsurf** | Copy `.windsurf/rules/project-walkthrough.md` → `.windsurf/rules/` |
| **OpenCode** | Copy `.opencode/skills/ruyi-project-walkthrough/` → `.opencode/skills/` |
| **Gemini CLI** | `gemini skills install https://github.com/zwyin/project-walkthrough-skill.git --path skills/project-walkthrough` |

## Output

```
<prefix>_project_study_<name>-<depth>-<lang>-<audience>/
├── docs/
│   ├── 01-overview.md
│   ├── 02-*.md
│   └── sources-manifest.json
└── interactive/
    └── walkthrough.html
```

## Key Features

- **Manifest-first accuracy**: Every claim verified against source before writing
- **8 project templates**: AI Tool, Library, Web App, CLI, Document, Game Engine, Database, Compiler
- **Source citations**: `// Simplified from: path:lines` on every code block
- **Self-contained HTML**: DOM-only (no innerHTML), responsive, print-friendly

## Full Documentation

See `skills/ruyi-project-walkthrough/SKILL.md` for the complete workflow specification.
