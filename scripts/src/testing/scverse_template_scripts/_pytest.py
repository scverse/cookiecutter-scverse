"""Temporary directory and git fixtures"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from . import GitRepo

if TYPE_CHECKING:
    from collections.abc import Generator


@pytest.fixture
def git_repo(
    tmp_path_factory: pytest.TempPathFactory,
) -> Generator[GitRepo, None, None]:
    tmp_path = tmp_path_factory.mktemp("git_repo")
    with GitRepo(tmp_path) as repo:
        yield repo
