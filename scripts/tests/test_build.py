from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from cookiecutter.main import cookiecutter

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any


HERE = Path(__file__).parent


@pytest.mark.parametrize(
    ("params", "path", "pattern"),
    [
        pytest.param({}, "docs/conf.py", r'"github_repo": project,', id="no_gh_repo"),
        pytest.param({"github_repo": "floob"}, "docs/conf.py", r'"github_repo": "floob",', id="gh_repo"),
        pytest.param({}, ".vscode/extensions.json", r'"ms-python.python",', id="no_ide_integ"),
        pytest.param({"ide_integration": False}, ".vscode", None, id="ide_integ"),
        pytest.param({}, ".github/ISSUE_TEMPLATE/bug_report.yml", r"^labels: bug$", id="default_labels"),
        pytest.param(
            {"issue_categorization": "labels"},
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            r"^labels: enhancement$",
            id="labels",
        ),
        pytest.param(
            {"issue_categorization": "issue types"},
            ".github/ISSUE_TEMPLATE/bug_report.yml",
            r"^type: Bug$",
            id="issue_types_bug",
        ),
        pytest.param(
            {"issue_categorization": "issue types"},
            ".github/ISSUE_TEMPLATE/feature_request.yml",
            r"^type: Enhancement$",
            id="issue_types_feature",
        ),
    ],
)
def test_build(tmp_path: Path, params: Mapping[str, Any], path: Path | str, pattern: re.Pattern | str | None) -> None:
    cookiecutter(str(HERE.parent.parent), output_dir=tmp_path, no_input=True, extra_context=params)
    proj_dir = tmp_path / "project-name"
    assert proj_dir.is_dir()
    path = proj_dir / path
    if pattern is None:
        assert not path.exists()
    else:
        pattern = re.compile(pattern, re.MULTILINE)
        assert pattern.search(path.read_text())

    assert not list(proj_dir.rglob("DELETE-ME"))


def test_build_without_global_git_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Generation must succeed without a global/system git identity (see issue #389).

    Users who configure git per-repository only have no global ``user.name``/``user.email``.
    In that case the hooks should fall back to the cookiecutter ``author_full_name``/
    ``author_email`` answers so the initial commit still succeeds.
    """
    # Neutralize any global/system git config so no ambient git identity is available.
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.setenv("GIT_CONFIG_SYSTEM", os.devnull)

    cookiecutter(
        str(HERE.parent.parent),
        output_dir=tmp_path,
        no_input=True,
        extra_context={"author_full_name": "Jane Doe", "author_email": "jane@example.com"},
    )
    proj_dir = tmp_path / "project-name"
    assert proj_dir.is_dir()

    # The initial commit must exist and be authored by the cookiecutter answers.
    author = subprocess.run(
        ["git", "-C", str(proj_dir), "log", "-1", "--format=%an <%ae>"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    assert author == "Jane Doe <jane@example.com>"
