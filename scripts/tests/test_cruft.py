from __future__ import annotations

import os
from pathlib import Path

import pytest

from scverse_template_scripts.cruft_prs import (
    GitHubConnection,
    _apply_update,
    _clone_and_prepare_repo,
    _commit_update,
    _get_cruft_config_from_upstream,
    get_repo_urls,
    get_template_release,
)


@pytest.fixture
def cookiecutter_scverse_instance_repo(scverse_bot_github_con):
    return scverse_bot_github_con.gh.get_repo("scverse/cookiecutter-scverse-instance")


@pytest.fixture
def cookiecutter_scverse_instance_repo_fork(scverse_bot_github_con, cookiecutter_scverse_instance_repo):
    return scverse_bot_github_con.gh.get_repo("scverse-bot/cookiecutter-scverse-instance")


@pytest.fixture
def cookiecutter_scverse_instance_cloned_repo(
    tmp_path, scverse_bot_github_con, cookiecutter_scverse_instance_repo, cookiecutter_scverse_instance_repo_fork
):
    clone_dir = tmp_path / "clone"
    repo = _clone_and_prepare_repo(
        scverse_bot_github_con,
        clone_dir,
        cookiecutter_scverse_instance_repo_fork,
        cookiecutter_scverse_instance_repo,
        "test-template-update-branch",
    )
    return repo


@pytest.fixture
def current_repo_path():
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


@pytest.fixture
def scverse_bot_github_con() -> GitHubConnection:
    """Connect to the scverse-bot github account. Make sure to use only a readonly-token to not destroy anything."""
    token = os.environ["SCVERSE_BOT_READONLY_GITHUB_TOKEN"]
    return GitHubConnection("scverse-bot", token, email="108668866+scverse-bot@users.noreply.github.com")


@pytest.mark.parametrize("tag_name", ["v0.4.0", "v0.2.17"])
def test_get_template_release(scverse_bot_github_con, tag_name):
    """Test if reference to release can be obtained"""
    release = get_template_release(scverse_bot_github_con.gh, tag_name)
    assert release.tag_name == tag_name


def test_get_repo_urls(scverse_bot_github_con):
    """Test if lits of repos using template can be obtained from scverse/ecosystem-packages"""
    repo_urls = get_repo_urls(scverse_bot_github_con.gh)
    assert any("scverse/scirpy" in url for url in repo_urls)


def test_clone_and_prepare_repo(cookiecutter_scverse_instance_cloned_repo):
    """Test that example repo can be cloned an all branches setup correctly"""
    repo = cookiecutter_scverse_instance_cloned_repo
    assert (Path(repo.working_dir) / "pyproject.toml").exists()
    assert repo.active_branch.name == "test-template-update-branch"
    assert repo.remote("upstream").url.endswith("github.com/scverse/cookiecutter-scverse-instance.git")
    assert repo.remote().url.endswith("github.com/scverse-bot/cookiecutter-scverse-instance.git")


def test_get_cruft_config_from_upstream(cookiecutter_scverse_instance_cloned_repo):
    config = _get_cruft_config_from_upstream(cookiecutter_scverse_instance_cloned_repo, "main")
    assert config["context"]["cookiecutter"]["project_name"] == "cookiecutter-scverse-instance"


def test_apply_update(cookiecutter_scverse_instance_cloned_repo, current_repo_path, tmp_path):
    log_file = tmp_path / "cruft_log.txt"
    _apply_update(
        cookiecutter_scverse_instance_cloned_repo,
        template_tag_name="main",
        cruft_log_file=log_file,
        cookiecutter_config={"project_name": "cookiecutter-scverse-instance"},
        template_url=str(current_repo_path),
    )


@pytest.mark.parametrize(
    "exclude_files,expected_untracked",
    [
        ([], []),
        (["doesntexist.txt"], []),
        (["dir1/A.txt", "dir1/doesntexist.txt"], ["dir1/A.txt"]),
        (["dir2/**.txt"], ["dir2/foo/A.txt", "dir2/foo/B.txt", "dir2/bar/C.txt", "dir2/D.txt"]),
        (["dir2/*"], ["dir2/foo/A.txt", "dir2/foo/B.txt", "dir2/bar/C.txt", "dir2/D.txt"]),
    ],
)
def test_commit_update(cookiecutter_scverse_instance_cloned_repo, exclude_files, expected_untracked):
    repo_dir = Path(cookiecutter_scverse_instance_cloned_repo.working_dir)
    (repo_dir / "dir1").mkdir()
    (repo_dir / "dir2").mkdir()
    (repo_dir / "dir2/foo").mkdir()
    (repo_dir / "dir2/bar").mkdir()
    (repo_dir / "dir1/A.txt").touch()
    (repo_dir / "dir2/foo/A.txt").touch()
    (repo_dir / "dir2/foo/B.txt").touch()
    (repo_dir / "dir2/bar/C.txt").touch()
    (repo_dir / "dir2/D.txt").touch()

    status = _commit_update(
        cookiecutter_scverse_instance_cloned_repo,
        exclude_files=exclude_files,
        commit_msg="foo",
        commit_author="scverse-bot",
    )

    # some files have changed and commit has been made
    assert status is True

    assert sorted(cookiecutter_scverse_instance_cloned_repo.untracked_files) == sorted(expected_untracked)


def test_commit_update_no_files(cookiecutter_scverse_instance_cloned_repo):
    assert (
        _commit_update(cookiecutter_scverse_instance_cloned_repo, commit_msg="foo", commit_author="scverse-bot")
        is False
    )
