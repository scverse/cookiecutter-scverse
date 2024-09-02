from __future__ import annotations

import re
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
        ({}, "docs/conf.py", r'"github_repo": project_name,'),
        ({"github_repo": "floob"}, "docs/conf.py", r'"github_repo": "floob",'),
    ],
)
def test_build(tmp_path: Path, params: Mapping[str, Any], path: Path | str, pattern: re.Pattern | str):
    cookiecutter(str(HERE.parent.parent), output_dir=tmp_path, no_input=True, extra_context=params)
    proj_dir = tmp_path / "project-name"
    assert proj_dir.is_dir()
    path = proj_dir / path
    pattern = re.compile(pattern, re.MULTILINE)
    assert pattern.search(path.read_text())
