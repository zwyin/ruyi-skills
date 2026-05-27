import pathlib
import pytest

SKILL_MD = pathlib.Path(__file__).parent.parent / "skills" / "ruyi-github-safe-publish" / "SKILL.md"
SCANNING_RULES_MD = pathlib.Path(__file__).parent.parent / "docs" / "scanning-rules.md"


def _parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end == -1:
        return {}
    raw = text[3:end]
    result = {}
    for line in raw.strip().splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


@pytest.fixture
def skill_text():
    return SKILL_MD.read_text(encoding="utf-8")


@pytest.fixture
def skill_frontmatter(skill_text):
    return _parse_frontmatter(skill_text)


@pytest.fixture
def rules_text():
    return SCANNING_RULES_MD.read_text(encoding="utf-8")
