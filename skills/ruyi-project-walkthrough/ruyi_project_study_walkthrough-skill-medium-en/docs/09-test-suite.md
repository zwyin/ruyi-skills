# Test Suite Architecture

The project has 8 test files totaling ~2,778 lines, covering output structure, manifest validation, dependency graphs, adaptive scope, language modes, platform conversion, watermarks, and release scripts.

## Test Files Overview

| File | Lines | Focus Area |
|------|-------|-----------|
| `test_walkthrough_output.py` | 861 | Output structure validation |
| `test_verify_sources.py` | 611 | Manifest verification |
| `test_import_graph.py` | 534 | Dependency graph extraction |
| `test_adaptive_scope.py` | 284 | Phase 0 scope/depth logic |
| `test_lang_output.py` | 170 | Multi-language output |
| `test_convert.py` | 152 | Platform file generation |
| `test_watermark.py` | 121 | Watermark/promo page |
| `test_release_sh.py` | 45 | Release script validation |

```text
// Simplified from: tests/test_walkthrough_output.py:1-11
"""
project-walkthrough skill output validation tests

Based on SKILL.md spec, validates walkthrough output structure and quality.
Test targets: tests/fixtures/ (CI) or examples/ (local dev)
"""
```

## Test Categories

### Output Structure (test_walkthrough_output.py)

The largest test file validates that generated walkthroughs follow the SKILL.md output structure specification:

```python
// Simplified from: tests/test_walkthrough_output.py:32-49
class TestDirectoryStructure:
    """SKILL.md Output Structure spec validation"""

    def test_examples_dir_exists(self):
        assert EXAMPLES_DIR.is_dir()

    def test_has_docs_dir(self, all_project_dir):
        assert (all_project_dir / "docs").is_dir()

    def test_has_interactive_dir(self, all_project_dir):
        assert (all_project_dir / "interactive").is_dir()

    def test_brief_docs_in_docs_flat(self, all_project_dir):
        """Brief level md files should be directly in docs/, not subdirectory"""
        brief_files = [f for f in docs.iterdir() if f.is_file() and f.suffix == ".md"]
        assert len(brief_files) >= 5
```

Tests check directory layout, file naming (`NN-kebab-case.md`), navigation links between chapters, HTML structure, manifest presence, and quiz validity.

### Manifest Verification (test_verify_sources.py)

Tests the `verify_sources.py` validation logic:

```python
// Simplified from: tests/test_verify_sources.py:36-56
def _make_minimal_manifest(**overrides):
    """Return a valid minimal manifest (non-strict mode)."""
    manifest = {
        "schema_version": "1.0",
        "source_project": {"name": "test-project", "repo_url": "https://example.com"},
        "generated_at": "2025-01-01T00:00:00Z",
        "claims": [
            {
                "id": "claim-001",
                "type": "code_example",
                "source_file": "src/main.py",
                "claim_summary": "A claim.",
                "verified": True,
            }
        ],
    }
```

Covers both strict mode (requires `doc_file`/`doc_line`) and non-strict mode (Phase 3A intermediate state).

### Import Graph (test_import_graph.py)

534 lines testing multi-language import extraction:

- Python relative and absolute imports
- TypeScript `import`, `require`, dynamic imports
- Rust `use`, `crate::`, `super::`, `mod` declarations
- Module grouping with depth control
- Parallel sibling detection

### Adaptive Scope (test_adaptive_scope.py)

284 lines testing Phase 0 logic:

- Content type detection signals
- Scope measurement and recommendations
- YAML format validation for analysis.md
- EXTEND.md preference loading

### Language Output (test_lang_output.py)

170 lines testing the 4 language modes:

- Chinese body + English terms (`zh`)
- Pure Chinese (`zh-pure`)
- Pure English (`en`)
- Bilingual side-by-side

### Platform Conversion (test_convert.py)

152 lines testing `convert.sh` output:

- Cursor `.mdc` format generation
- Windsurf condensed output under 12K chars
- OpenCode SKILL.md generation
- Sync checking between canonical and platform files

## Test Strategy

Tests use a dual-fixture approach:

```python
// Simplified from: tests/test_walkthrough_output.py:19-27
SKILL_ROOT = Path(__file__).parent.parent
EXAMPLES_DIR = (SKILL_ROOT / "tests" / "fixtures") if (SKILL_ROOT / "tests" / "fixtures").is_dir() and any((SKILL_ROOT / "tests" / "fixtures").iterdir()) else (SKILL_ROOT / "examples")

FULL_PROJECTS = [p for p in _CANDIDATE_FULL if (EXAMPLES_DIR / p).is_dir()]
BRIEF_ONLY_PROJECTS = [p for p in _CANDIDATE_BRIEF if (EXAMPLES_DIR / p).is_dir()]
```

CI uses `tests/fixtures/` (if available), otherwise falls back to `examples/`. Projects are classified as "full" (brief + medium + deep) or "brief only" based on which output levels exist.

## Running Tests

```bash
pytest tests/ -v           # Verbose output
pytest tests/ -q           # Quiet mode
make test                  # Via Makefile
make test-quick            # Quick mode
make ci                    # Full CI: test + convert.sh --check
```

[Previous: Version Management](08-version-release.md) | [Next: Interactive HTML UX](10-interactive-html-ux.md)
