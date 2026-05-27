"""Tests for watermark (promo page) feature in md_to_html.py."""

import pytest
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from md_to_html import build_watermark_section, build_html

SCRIPT = Path(__file__).parent.parent / "scripts" / "md_to_html.py"

# Minimal chapter data for build_html
ONE_CHAPTER = [{"title": "Intro", "sidebar": "01 Intro", "html": "<h1>Intro</h1><p>Hello</p>"}]


class TestBuildWatermarkSection:
    def test_zh_default(self):
        html = build_watermark_section("ruyi-project-walkthrough", "https://github.com/zwyin/ruyi-skills", "zh")
        assert 'id="ch-watermark"' in html
        assert "关于本报告" in html
        assert "<strong>ruyi-project-walkthrough</strong>" in html
        assert "https://github.com/zwyin/ruyi-skills" in html
        assert "欢迎大家使用、讨论和反馈" in html

    def test_en(self):
        html = build_watermark_section("davinci-project-walkthrough", "https://github.com/zwyin/davinci-skills", "en")
        assert "About This Report" in html
        assert "<strong>davinci-project-walkthrough</strong>" in html
        assert "https://github.com/zwyin/davinci-skills" in html
        assert "Feedback and contributions are welcome!" in html

    def test_bilingual(self):
        html = build_watermark_section("test-tool", "https://example.com", "bilingual")
        assert "About This Report" in html
        assert "<strong>test-tool</strong>" in html

    def test_no_url(self):
        html = build_watermark_section("test-tool", None, "zh")
        assert "id=\"ch-watermark\"" in html
        assert "<strong>test-tool</strong>" in html
        assert "href=" not in html

    def test_contains_utc_timestamp(self):
        html = build_watermark_section("t", "https://x.com", "zh")
        current_year = str(datetime.now(timezone.utc).year)
        assert current_year in html


class TestBuildHtmlWithWatermark:
    def test_with_watermark_adds_sidebar_link(self):
        result = build_html(ONE_CHAPTER, "#4a6fa5", "Test", "zh", "", '<div class="chapter" id="ch-watermark"><p>promo</p></div>')
        assert 'id="ch-watermark"' in result
        # Sidebar should have 2 links: chapter + watermark
        assert result.count("showChapter(") >= 2

    def test_without_watermark_no_promo(self):
        result = build_html(ONE_CHAPTER, "#4a6fa5", "Test", "zh", "", "")
        assert "ch-watermark" not in result

    def test_watermark_after_quiz(self):
        quiz_html = '<div class="chapter" id="ch-quiz"><p>quiz</p></div>'
        wm_html = '<div class="chapter" id="ch-watermark"><p>promo</p></div>'
        result = build_html(ONE_CHAPTER, "#4a6fa5", "Test", "zh", quiz_html, wm_html)
        # All three should be present
        assert 'id="ch0"' in result
        assert 'id="ch-quiz"' in result
        assert 'id="ch-watermark"' in result
        # Sidebar: chapter + quiz + watermark = 3 nav items
        assert result.count("showChapter(") >= 3

    def test_last_chapter_next_points_to_watermark(self):
        wm_html = '<div class="chapter" id="ch-watermark"><p>promo</p></div>'
        result = build_html(ONE_CHAPTER, "#4a6fa5", "Test", "zh", "", wm_html)
        # The chapter's Next link should point to the watermark chapter
        assert "showChapter(1)" in result


class TestWatermarkCLI:
    """End-to-end tests running md_to_html.py as subprocess."""

    @pytest.fixture
    def docs_dir(self, tmp_path):
        d = tmp_path / "docs"
        d.mkdir()
        (d / "01-intro.md").write_text("# Intro\nHello world\n")
        return d

    def test_default_has_watermark(self, docs_dir, tmp_path):
        out = tmp_path / "out.html"
        r = subprocess.run(
            [sys.executable, str(SCRIPT), str(docs_dir), str(out),
             "--title", "Test", "--tool-name", "my-tool",
             "--tool-url", "https://example.com"],
            capture_output=True, text=True)
        assert r.returncode == 0
        html = out.read_text()
        assert "ch-watermark" in html
        assert "my-tool" in html
        assert "https://example.com" in html

    def test_no_watermark_flag(self, docs_dir, tmp_path):
        out = tmp_path / "out.html"
        r = subprocess.run(
            [sys.executable, str(SCRIPT), str(docs_dir), str(out),
             "--title", "Test", "--no-watermark"],
            capture_output=True, text=True)
        assert r.returncode == 0
        html = out.read_text()
        assert "ch-watermark" not in html
        assert "关于本报告" not in html

    def test_watermark_hidden_from_help(self):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--help"],
            capture_output=True, text=True)
        assert "--no-watermark" not in r.stdout
        assert "--tool-name" not in r.stdout
        assert "--tool-url" not in r.stdout
