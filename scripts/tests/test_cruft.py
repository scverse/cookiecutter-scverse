from __future__ import annotations

import os
import uuid

import git
import pytest

from scverse_template_scripts.cruft_prs import (
    GitHubConnection,
    get_fork,
    get_repo_urls,
    get_template_release,
    template_update,
)


@pytest.fixture
def cookiecutter_scverse_instance_repo(con):
    return con.gh.get_repo("scverse/cookiecutter-scverse-instance")


@pytest.fixture
def cookiecutter_scverse_instance_repo_fork(con, cookiecutter_scverse_instance_repo):
    return get_fork(con, cookiecutter_scverse_instance_repo)


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
def con() -> GitHubConnection:
    token = os.environ["GITHUB_TOKEN"]
    return GitHubConnection("scverse-bot", token, email="108668866+scverse-bot@users.noreply.github.com")


@pytest.mark.parametrize("tag_name", ["v0.4.0", "v0.2.17"])
def test_get_template_release(con, tag_name):
    """Test if reference to release can be obtained"""
    release = get_template_release(con.gh, tag_name)
    assert release.tag_name == tag_name


def test_get_repo_urls(con):
    """Test if lits of repos using template can be obtained from scverse/ecosystem-packages"""
    repo_urls = get_repo_urls(con.gh)
    assert any("scverse/scirpy" in url for url in repo_urls)


@pytest.mark.parametrize("repo_name", ["scverse/cookiecutter-scverse-instance"])
def test_get_fork(con, repo_name):
    """Test if a public repo can be forked into the scverse-bot namespace"""
    repo = con.gh.get_repo(repo_name)
    # try getting fork (create if not exist)
    get_fork(con, repo)


def test_update_template(
    con,
    cookiecutter_scverse_instance_repo,
    cookiecutter_scverse_instance_repo_fork,
    tmp_path,
    template_update_branch_name,
):
    # Get latest commit from local git repository using GitPython
    repo = git.Repo(os.getcwd())
    latest_commit = repo.head.commit.hexsha

    template_update(
        con,
        forked_repo=cookiecutter_scverse_instance_repo_fork,
        template_branch_name=template_update_branch_name,
        original_repo=cookiecutter_scverse_instance_repo,
        workdir=tmp_path,
        tag_name=latest_commit,
        cruft_log_file=tmp_path / "cruft_log.txt",
    )
