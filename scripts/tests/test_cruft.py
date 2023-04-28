from dataclasses import dataclass
from typing import cast

import pytest
from github.GitRelease import GitRelease as GHRelease
from github.Repository import Repository as GHRepo
from pytest_git import GitRepo
from scverse_template_scripts.cruft_prs import PR, GitHubConnection, cruft_update


@dataclass
class MockGHRepo:
    git_url: str  # git://github.com/foo/bar.git
    clone_url: str  # https://github.com/foo/bar.git


@dataclass
class MockRelease:
    tag_name: str = "test-tag"
    title: str = "A test release"
    body: str = "* Some changelog entry"
    html_url: str = "https://example.com"


@pytest.fixture
def con() -> GitHubConnection:
    return GitHubConnection("testuser", "test@example.com")


@pytest.fixture
def repo(git_repo: GitRepo) -> GHRepo:
    return cast(GHRepo, MockGHRepo(git_repo.uri, git_repo.uri))


@pytest.fixture
def pr() -> PR:
    return PR(cast(GHRelease, MockRelease()))


def test_cruft_update(con, repo, tmp_path, pr):
    changed = cruft_update(con, repo, tmp_path, pr)
    assert changed
