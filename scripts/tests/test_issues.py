from __future__ import annotations

from scverse_template_scripts.template_issues import (
    issue_marker,
    issue_title,
    parse_issue_tag,
    skill_urls,
)


def test_marker_roundtrip() -> None:
    tag = "v0.6.0"
    body = f"some text\n\n{issue_marker(tag)}\n"
    assert parse_issue_tag(body) == tag


def test_parse_issue_tag_absent() -> None:
    assert parse_issue_tag(None) is None
    assert parse_issue_tag("a regular issue with no marker") is None


def test_title_contains_tag() -> None:
    assert "v1.2.3" in issue_title("v1.2.3")


def test_skill_urls_pin_to_tag() -> None:
    skill_md, helper = skill_urls("scverse/cookiecutter-scverse", "v0.6.0")
    assert skill_md == (
        "https://github.com/scverse/cookiecutter-scverse/blob/v0.6.0/.claude/skills/scverse-template-update/SKILL.md"
    )
    assert helper.startswith("https://raw.githubusercontent.com/scverse/cookiecutter-scverse/v0.6.0/")
    assert helper.endswith("/sync_helper.py")
