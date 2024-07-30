"""Temporary directory and git fixtures"""

from __future__ import annotations

import pytest

from . import GitRepo


@pytest.fixture
def git_repo(
    tmp_path_factory: pytest.TempPathFactory,
) -> GitRepo:
    tmp_path = tmp_path_factory.mktemp("git_repo")
    return GitRepo(tmp_path)
