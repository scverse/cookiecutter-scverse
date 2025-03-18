from __future__ import annotations

import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast
from warnings import catch_warnings

import pytest

from scverse_template_scripts.cruft_prs import GitHubConnection, TemplateUpdatePR, cruft_update

if TYPE_CHECKING:
    from pathlib import Path

    from git import Commit, Diff
    from github.GitRelease import GitRelease as GHRelease
    from github.Repository import Repository as GHRepo

    from testing.scverse_template_scripts import GitRepo


@dataclass
class MockGHRepo:
    git_url: str  # git://github.com/foo/bar.git
    clone_url: str  # https://github.com/foo/bar.git
    default_branch: str  # main


@dataclass
class MockRelease:
    tag_name: str = "test-tag"
    title: str = "A test release"
    body: str = "* Some changelog entry"
    html_url: str = "https://example.com"


@pytest.fixture
def con(response_mock) -> GitHubConnection:
    resp = json.dumps({"login": "scverse-bot"})
    with catch_warnings(), response_mock(f"GET https://api.github.com:443/users/scverse-bot -> 200 :{resp}"):
        return GitHubConnection("scverse-bot")


@pytest.fixture
def repo(git_repo: GitRepo) -> GHRepo:
    assert not git_repo.api.bare
    (git_repo.workspace / "a").write_text("a content")
    (git_repo.workspace / "b").write_text("b content")
    git_repo.api.index.add(["a", "b"])
    git_repo.api.index.commit("initial commit")
    return cast("GHRepo", MockGHRepo(git_repo.uri, git_repo.uri, "main"))


@pytest.fixture
def pr(con) -> TemplateUpdatePR:
    return TemplateUpdatePR(con, cast("GHRelease", MockRelease()), "scverse-test")


def test_cruft_update(con, repo, tmp_path, pr, git_repo: GitRepo, monkeypatch: pytest.MonkeyPatch):
    old_active_branch_name = git_repo.api.active_branch.name

    def _mock_run_cruft(cwd: Path, *, tag_name, log_name):
        return (cwd / "b").write_text("b modified")

    monkeypatch.setattr("scverse_template_scripts.cruft_prs.run_cruft", _mock_run_cruft)
    changed = cruft_update(con, pr, tag_name="main", repo=repo, origin=repo, path=tmp_path)
    assert changed  # TODO: add test for short circuit
    main_branch = git_repo.api.active_branch
    assert main_branch.name == old_active_branch_name, "Shouldn’t change active branch"
    pr_branch = next(b for b in git_repo.api.branches if b.name == pr.branch)
    commit = cast("Commit", pr_branch.commit)
    assert list(commit.parents) == [main_branch.commit]
    assert [
        (diff.change_type, diff.a_path, diff.b_path) for diff in cast("list[Diff]", main_branch.commit.diff(commit))
    ] == [("M", "b", "b")]
