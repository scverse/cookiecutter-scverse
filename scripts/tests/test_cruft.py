from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from git.repo.base import Repo
from github.Repository import Repository

from scverse_template_scripts.cruft_prs import (
    GitHubConnection,
    _apply_update,
    _clone_and_prepare_repo,
    _commit_update,
    _get_cruft_config_from_upstream,
    get_repo_urls,
    get_template_release,
)

if TYPE_CHECKING:
    from git import Repo
    from github.Repository import Repository


@pytest.fixture
def bot_con() -> GitHubConnection:
    """Connect to the scverse-bot github account. Make sure to use only a readonly-token to not destroy anything."""
    token = os.environ["SCVERSE_BOT_READONLY_GITHUB_TOKEN"]
    return GitHubConnection("scverse-bot", token, email="108668866+scverse-bot@users.noreply.github.com")


@pytest.fixture
def instance_orig(bot_con: GitHubConnection) -> Repository:
    return bot_con.gh.get_repo("scverse/cookiecutter-scverse-instance")


@pytest.fixture
def instance_fork(bot_con: GitHubConnection, instance_orig: Repository) -> Repository:
    del instance_orig  # included for the side effect
    return bot_con.gh.get_repo("scverse-bot/cookiecutter-scverse-instance")


@pytest.fixture
def clone(tmp_path: Path, bot_con: GitHubConnection, instance_orig: Repository, instance_fork: Repository) -> Repo:
    clone_dir = tmp_path / "clone"
    return _clone_and_prepare_repo(
        bot_con,
        clone_dir,
        "test-template-update-branch",
        forked_repo=instance_fork,
        original_repo=instance_orig,
    )


@pytest.fixture
def current_repo_path() -> Path:
    """Get the currently checked out commit hash of this repository"""
    repo_path = Path(__file__).resolve()
    while True:
        git_dir = repo_path / ".git"
        if git_dir.exists():
            break
        if repo_path == repo_path.parent:
            msg = "Could not find .git directory"
            raise ValueError(msg)
        repo_path = repo_path.parent

    return repo_path


@pytest.mark.parametrize("tag_name", ["v0.4.0", "v0.2.17"])
def test_get_template_release(bot_con: GitHubConnection, tag_name: str) -> None:
    """Test if reference to release can be obtained"""
    release = get_template_release(bot_con.gh, tag_name)
    assert release.tag_name == tag_name


def test_get_repo_urls(bot_con: GitHubConnection) -> None:
    """Test if lits of repos using template can be obtained from scverse/ecosystem-packages"""
    repo_urls = get_repo_urls(bot_con.gh)
    assert any("scverse/scirpy" in url for url in repo_urls)


def test_clone_and_prepare_repo(clone: Repo) -> None:
    """Test that example repo can be cloned an all branches setup correctly"""
    assert (Path(clone.working_dir) / "pyproject.toml").exists()
    assert clone.active_branch.name == "test-template-update-branch"
    assert clone.remote("upstream").url.endswith("github.com/scverse/cookiecutter-scverse-instance.git")
    assert clone.remote().url.endswith("github.com/scverse-bot/cookiecutter-scverse-instance.git")


def test_get_cruft_config_from_upstream(clone: Repo) -> None:
    config = _get_cruft_config_from_upstream(clone, "main")
    assert config["context"]["cookiecutter"]["project_name"] == "cookiecutter-scverse-instance"


def test_apply_update(clone: Repo, current_repo_path: Path, tmp_path: Path) -> None:
    """Test that a template update can be applied to a cloned repo without crashing"""
    log_file = tmp_path / "cruft_log.txt"
    _apply_update(
        clone,
        template_tag_name=None,
        cruft_log_file=log_file,
        cookiecutter_config={"project_name": "cookiecutter-scverse-instance"},
        template_url=str(current_repo_path),
    )


@pytest.mark.parametrize(
    ("exclude_files", "expected_untracked"),
    [
        ([], []),
        (["doesntexist.txt"], []),
        (["dir1/A.txt", "dir1/doesntexist.txt"], ["dir1/A.txt"]),
        (["dir2/**.txt"], ["dir2/foo/A.txt", "dir2/foo/B.txt", "dir2/bar/C.txt", "dir2/D.txt"]),
        (["dir2/*"], ["dir2/foo/A.txt", "dir2/foo/B.txt", "dir2/bar/C.txt", "dir2/D.txt"]),
    ],
)
def test_commit_update(clone: Repo, exclude_files: list[str], expected_untracked: list[str]) -> None:
    repo_dir = Path(clone.working_dir)
    (repo_dir / "dir1").mkdir()
    (repo_dir / "dir2").mkdir()
    (repo_dir / "dir2/foo").mkdir()
    (repo_dir / "dir2/bar").mkdir()
    (repo_dir / "dir1/A.txt").touch()
    (repo_dir / "dir2/foo/A.txt").touch()
    (repo_dir / "dir2/foo/B.txt").touch()
    (repo_dir / "dir2/bar/C.txt").touch()
    (repo_dir / "dir2/D.txt").touch()

    status = _commit_update(clone, exclude_files=exclude_files, commit_msg="foo", commit_author="scverse-bot")

    # some files have changed and commit has been made
    assert status is True

    assert sorted(clone.untracked_files) == sorted(expected_untracked)


def test_commit_update_no_files(clone: Repo) -> None:
    assert _commit_update(clone, commit_msg="foo", commit_author="scverse-bot") is False
