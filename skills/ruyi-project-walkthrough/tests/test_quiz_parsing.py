"""Tests for quiz markdown parsing in md_to_html.py.

Regression coverage for parse_quiz_md: the correct-answer index (`c`) must
reflect the letter in the `**Answer: X**` line, not always default to 0.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))
from md_to_html import parse_quiz_md  # noqa: E402


def _quiz_md(*questions):
    """Build a quiz markdown body from (q_text, opts_list, answer_letter, explanation)."""
    parts = []
    for i, (q, opts, ans, expl) in enumerate(questions, 1):
        letters = "ABCD"
        opt_lines = "\n".join(f"- {letters[j]}. {o}" for j, o in enumerate(opts))
        parts.append(
            f"**Q{i}:** {q}\n{opt_lines}\n\n**Answer: {ans}**\n\n**Explanation:** {expl}\n\n---\n"
        )
    return "".join(parts)


def _parse(questions):
    return parse_quiz_md(_quiz_md(*questions))


def test_answer_b_yields_index_1():
    """Core regression: Answer: B must map to index 1, not 0.

    Previously `re.search(r'([A-D])', '**Answer: B**')` matched the 'A' inside
    the word "Answer", so every question's correct index collapsed to 0.
    """
    qs = _parse([
        ("q?", ["aa", "bb", "cc", "dd"], "B", "b is right"),
    ])
    assert len(qs) == 1
    assert qs[0]["c"] == 1, f"Answer B -> index 1, got {qs[0]['c']}"
    assert qs[0]["o"][qs[0]["c"]] == "bb"


def test_answer_a_yields_index_0():
    qs = _parse([("q?", ["aa", "bb", "cc", "dd"], "A", "a is right")])
    assert qs[0]["c"] == 0


def test_answer_c_yields_index_2():
    qs = _parse([("q?", ["aa", "bb", "cc", "dd"], "C", "c is right")])
    assert qs[0]["c"] == 2


def test_answer_d_yields_index_3():
    qs = _parse([("q?", ["aa", "bb", "cc", "dd"], "D", "d is right")])
    assert qs[0]["c"] == 3


def test_answer_with_chinese_colon():
    """SKILL.md allows both ':' and '：' as the Answer colon."""
    body = (
        "**Q1:** q?\n"
        "- A. aa\n- B. bb\n- C. cc\n- D. dd\n\n"
        "**Answer：C**\n\n"
        "**Explanation:** c.\n"
    )
    qs = parse_quiz_md(body)
    assert qs[0]["c"] == 2


def test_mixed_answers_across_questions():
    """A realistic quiz where each question has a different correct letter.

    This is the case that was 100% broken: every c collapsed to 0 regardless
    of the actual answer letter.
    """
    qs = _parse([
        ("q1?", ["a1", "b1", "c1", "d1"], "B", "x"),
        ("q2?", ["a2", "b2", "c2", "d2"], "D", "x"),
        ("q3?", ["a3", "b3", "c3", "d3"], "A", "x"),
        ("q4?", ["a4", "b4", "c4", "d4"], "C", "x"),
    ])
    assert [q["c"] for q in qs] == [1, 3, 0, 2], (
        f"expected [1,3,0,2], got {[q['c'] for q in qs]}"
    )


def test_explanation_and_question_preserved():
    qs = _parse([("the question?", ["aa", "bb", "cc", "dd"], "B", "the why")])
    assert qs[0]["q"] == "the question?"
    assert qs[0]["e"] == "the why"
