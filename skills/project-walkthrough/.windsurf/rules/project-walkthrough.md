---
trigger: model_decision
description: "Use when the user wants to study, document, understand, or share analysis of a software project/codebase. Triggers on requests like 'walk through this project', 'explain this codebase', 'generate documentation for this project', 'help me understand this code'."
---
# Project Walkthrough Generator

Generate a structured walkthrough of any project — software codebase, research report, or document collection. Adapts output scope to input size and content type.

> **Version 1.6.0** — Shown at Phase 0 startup. Use `--version` to print version and exit.

## User Input Tools

When this skill prompts the user, follow this tool-selection rule (priority order):

1. **Prefer built-in user-input tools** — e.g., `AskUserQuestion`, `request_user_input`, `clarify`, `ask_user`, or equivalent.
2. **Fallback**: if no such tool exists, emit a numbered plain-text message and ask the user to reply with the chosen number/answer for each question.
3. **Batching**: if the tool supports multiple questions per call, combine all applicable questions into a single call; if only single-question, ask them one at a time.

## Usage

```
/project-walkthrough [path] [--depth brief|medium|deep|all] [--audience general|dev] [--lang zh|zh-pure|en|bilingual] [--no-confirm] [--version]
```

**Argument parsing:** Parse `$ARGUMENTS` using `--flag` convention:

1. Split `$ARGUMENTS` by whitespace into tokens; empty-string tokens are discarded; paths with spaces are not supported
2. Tokens starting with `--` are flags:
   - `--depth <value>` — sets depth (`brief`, `medium`, `deep`, `all`)
   - `--audience <value>` — sets audience (`general`, `dev`)
   - `--lang <value>` — sets output language (`zh`, `zh-pure`, `en`, `bilingual`)
   - `--no-confirm` — skip confirmation gate, use recommended defaults
   - `--version` — print version and exit (standalone, no value consumed)
   - Only space-separated `--flag value` syntax is supported (not `--flag=value`)
   - Flags are case-sensitive (`--Depth` is not `--depth`)
   - A flag always consumes exactly the next token as its value, regardless of what that token contains
   - If a flag is the last token (no value follows), ignore it and use the default
   - If the same flag appears multiple times, the **last** occurrence wins
   - Unknown `--` flags are ignored along with their immediately following token
   - `--no-confirm` is a standalone flag (no value consumed)
   - `--version` is a standalone flag (no value consumed); when present, print `project-walkthrough v1.6.1` and exit immediately
   - If a recognized flag receives an invalid value (not in the allowed set), discard the value and use the default
3. The first non-flag token that is not consumed as a flag value is the `path`
4. Additional non-flag tokens are ignored
5. Flags can appear before or after the path
6. Defaults: path → current working directory, depth → `brief`, audience → `general`, lang → `zh`, confirm → `true`
7. If `--version` is present, print `project-walkthrough v1.6.1` and stop — ignore all other flags and path

**Parameters:**
- `path` (positional, optional) — Project directory. Defaults to current working directory.
- `--depth` (optional) — One of: `brief`, `medium`, `deep`, `all`. Defaults to `brief`.
- `--audience` (optional) — One of: `general`, `dev`. Defaults to `general`.
- `--lang` (optional) — One of: `zh`, `zh-pure`, `en`, `bilingual`. Defaults to `zh`.
- `--no-confirm` (optional) — Skip Phase 0 confirmation gate.
- `--version` (optional) — Print version (`project-walkthrough v1.6.1`) and exit.

Invalid or missing flag values fall back to defaults. If a flag is repeated, the last occurrence wins.
