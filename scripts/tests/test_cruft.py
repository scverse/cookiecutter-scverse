from __future__ import annotations

import os
import uuid

import git
import pytest

from scverse_template_scripts.cruft_prs import (
    GitHubConnection,
    get_repo_urls,
    get_template_release,
    template_update,
)


@pytest.fixture
def cookiecutter_scverse_instance_repo(scverse_bot_github_con):
    return scverse_bot_github_con.gh.get_repo("scverse/cookiecutter-scverse-instance")


@pytest.fixture
def cookiecutter_scverse_instance_repo_fork(scverse_bot_github_con, cookiecutter_scverse_instance_repo):
    return scverse_bot_github_con.gh.get_repo("scverse-bot/cookiecutter-scverse-instance")


@pytest.fixture
def template_update_branch_name(cookiecutter_scverse_instance_repo_fork):
    branch_name = f"scverse-bot-ci-test:template-update-{uuid.uuid4()}"

    yield branch_name

    # Try to delete the branch if it exists
    try:
        ref = cookiecutter_scverse_instance_repo_fork.get_git_ref(f"heads/{branch_name}")
        ref.delete()
    except Exception:  # noqa
        # Branch doesn't exist yet, which is fine
        pass


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


def test_update_template(
    scverse_bot_github_con,
    cookiecutter_scverse_instance_repo,
    cookiecutter_scverse_instance_repo_fork,
    tmp_path,
    template_update_branch_name,
):
    # Get latest commit from local git repository using GitPython
    repo = git.Repo(os.getcwd())
    latest_commit = repo.head.commit.hexsha

    template_update(
        scverse_bot_github_con,
        forked_repo=cookiecutter_scverse_instance_repo_fork,
        template_branch_name=template_update_branch_name,
        original_repo=cookiecutter_scverse_instance_repo,
        workdir=tmp_path,
        tag_name=latest_commit,
        cruft_log_file=tmp_path / "cruft_log.txt",
    )
