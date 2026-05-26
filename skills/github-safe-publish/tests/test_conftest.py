"""Tests for test utilities (conftest.py coverage)."""
from tests.conftest import _parse_frontmatter


def test_parse_frontmatter_extracts_fields():
    text = '---\nname: foo\nversion: "1.0.0"\n---\nbody'
    result = _parse_frontmatter(text)
    assert result["name"] == "foo"
    assert result["version"] == "1.0.0"


def test_parse_frontmatter_no_fences():
    assert _parse_frontmatter("no frontmatter") == {}


def test_parse_frontmatter_unclosed_fence():
    assert _parse_frontmatter("---\nname: foo") == {}
