"""
Unit tests for Bug 1 fix: code-block citation coverage in verify_html.

verify_html now reports code_blocks / code_blocks_cited / code_blocks_uncited
and emits a warning when source-code blocks lack a // Simplified/Derived from:
citation. Untagged and ```text blocks (diagrams, output) are exempt.
"""

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(SKILL_ROOT / "scripts"))

from md_to_html import verify_html, build_html, convert_md_to_html  # noqa: E402


def _build_html(tmp_path, docs_dir):
    """Convert a docs dir into an HTML file (mirror what main() does), return path."""
    mds = sorted(Path(docs_dir).glob("*.md"))
    chapters = []
    for f in mds:
        t = f.read_text("utf-8")
        chapters.append({"title": "x", "sidebar": "x",
                         "html": convert_md_to_html(t)})
    html = build_html(chapters, "#4a6fa5", "Test", "zh")
    out = tmp_path / "out.html"
    out.write_text(html, "utf-8")
    return out


def test_uncited_source_code_block_is_flagged_as_warning(tmp_path):
    """A ```python block without a citation increments code_blocks_uncited and
    adds a warning, but does NOT fail (passed stays True)."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "01.md").write_text(
        "# Title\n\n"
        "```python\nprint('hi')\n```\n",  # uncited source-code block
        encoding="utf-8")
    html = _build_html(tmp_path, docs)
    code, result = verify_html(html, source_dir=docs)
    assert result["code_blocks"] == 1
    assert result["code_blocks_cited"] == 0
    assert result["code_blocks_uncited"] == 1
    assert any("Phase 3C" in w for w in result["warnings"])
    assert result["passed"] is True  # warning, not hard error


def test_cited_source_code_block_is_counted_as_cited(tmp_path):
    """A ```python block carrying // Simplified from: is counted as cited."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "01.md").write_text(
        "# Title\n\n"
        "```python\n# Simplified from: src/x.py:1-5\nprint('hi')\n```\n",
        encoding="utf-8")
    html = _build_html(tmp_path, docs)
    code, result = verify_html(html, source_dir=docs)
    assert result["code_blocks"] == 1
    assert result["code_blocks_cited"] == 1
    assert result["code_blocks_uncited"] == 0
    assert result["warnings"] == []


def test_text_and_untagged_blocks_are_exempt(tmp_path):
    """Diagrams (```text) and untagged blocks must NOT count as source code,
    so a chapter with only an ASCII diagram has code_blocks=0."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "01.md").write_text(
        "# Title\n\n"
        "```text\n+---+\n| A |\n+---+\n```\n\n"
        "```\nsome plain output\n```\n",
        encoding="utf-8")
    html = _build_html(tmp_path, docs)
    code, result = verify_html(html, source_dir=docs)
    assert result["code_blocks"] == 0
    assert result["code_blocks_uncited"] == 0


def test_mixed_cited_and_uncited_counted_separately(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "01.md").write_text(
        "# Title\n\n"
        "```python\n# Derived from: a.py:1-2\nx=1\n```\n\n"
        "```python\ny=2\n```\n\n"          # uncited
        "```json\n{\"k\":1}\n```\n",        # uncited, json counts as source
        encoding="utf-8")
    html = _build_html(tmp_path, docs)
    code, result = verify_html(html, source_dir=docs)
    assert result["code_blocks"] == 3
    assert result["code_blocks_cited"] == 1
    assert result["code_blocks_uncited"] == 2


def test_no_source_dir_leaves_uncited_null(tmp_path):
    """Without source_dir, the citation check is skipped (uncited is None)."""
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "01.md").write_text("# Title\n\n```python\nx=1\n```\n", encoding="utf-8")
    html = _build_html(tmp_path, docs)
    code, result = verify_html(html, source_dir=None)
    assert result["code_blocks_uncited"] is None
    assert result["warnings"] == []
