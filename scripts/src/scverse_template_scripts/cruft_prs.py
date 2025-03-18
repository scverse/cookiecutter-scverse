"""Script to send cruft update PRs.

Uses `template-repos.yml` from `scverse/ecosystem-packages`.
"""

from __future__ import annotations

import math
import os
import sys
from dataclasses import InitVar, dataclass, field
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, ClassVar, TypedDict, cast

from cyclopts import App
from furl import furl
from git.exc import GitCommandError
from git.repo import Repo
from git.util import Actor
from github import Github, UnknownObjectException
from yaml import safe_load

from ._log import log, setup_logging
from .backoff import retry_with_backoff

if TYPE_CHECKING:
    from collections.abc import Generator
    from subprocess import CompletedProcess
    from typing import IO, LiteralString, NotRequired

    from github import ContentFile
    from github.GitRelease import GitRelease as GHRelease
    from github.NamedUser import NamedUser
    from github.PullRequest import PullRequest
    from github.Repository import Repository as GHRepo

PR_BODY_TEMPLATE = """\
`cookiecutter-scverse` released [{release.tag_name}]({release.html_url}).

## Changes

{release.body}

## Additional remarks
* unsubscribe: If you don’t want to receive these PRs in the future,
  add `skip: true` to [`template-repos.yml`][] using a PR or,
  if you never want to sync from the template again, delete your `.cruft` file.
* If there are **merge conflicts**,
  they either show up inline (`>>>>>>>`) or a `.rej` file will have been created for the respective files.
  You need to address these conflicts manually. Make sure to enable pre-commit.ci (see below) to detect such files.
* The scverse template works best when the [pre-commit.ci][], [readthedocs][] and [codecov][] services are enabled.
  Make sure to activate those apps if you haven't already.

[`template-repos.yml`]: https://github.com/scverse/ecosystem-packages/blob/main/template-repos.yml
[pre-commit.ci]: {template_usage}#pre-commit-ci
[readthedocs]: {template_usage}#documentation-on-readthedocs
[codecov]: {template_usage}#coverage-tests-with-codecov
"""

# GitHub says that up to 5 minutes of wait are OK,
# So we error our once we wait longer, i.e. when 2ⁿ = 5 min × 60 sec/min
n_retries = math.ceil(math.log(5 * 60) / math.log(2))  # = ⌈~8.22⌉ = 9
# Due to exponential backoff, we’ll maximally wait 2⁹ sec, or 8.5 min


@dataclass
class GitHubConnection:
    """API connection to a github user (e.g. scverse-bot)"""

    login: InitVar[str]
    token: str | None = field(repr=False, default=None)
    gh: Github = field(init=False)
    user: NamedUser = field(init=False)
    sig: Actor = field(init=False)

    def __post_init__(self, login: str) -> None:
        self.gh = Github(self.token)
        self.user = self.gh.get_user(login)
        self.sig = Actor(self.login, self.email)

    @property
    def login(self) -> str:
        return self.user.login

    @property
    def email(self) -> str:
        return self.user.email

    def auth(self, url_str: str) -> str:
        url = furl(url_str)
        if self.token:
            url.username = self.token
        return str(url)


@dataclass
class PR:
    """A template-update pull request to a repository using the cookiecutter template"""

    con: GitHubConnection
    release: GHRelease
    repo_id: str  # something like grst-infercnvpy

    title_prefix: ClassVar[LiteralString] = "Update template to "
    branch_prefix: ClassVar[LiteralString] = "template-update-"

    @property
    def title(self) -> str:
        return f"{self.title_prefix}{self.release.tag_name}"

    @property
    def branch(self) -> str:
        return f"{self.branch_prefix}{self.repo_id}-{self.release.tag_name}"

    @property
    def namespaced_head(self) -> str:
        return f"{self.con.login}:{self.branch}"

    @property
    def body(self) -> str:
        return PR_BODY_TEMPLATE.format(
            release=self.release,
            template_usage="https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html",
        )

    def matches_prefix(self, pr: PullRequest) -> bool:
        """Check if `pr` is either a current or previous template update PR by matching the branch name"""
        # Don’t compare title prefix, people might rename PRs
        return pr.head.ref.startswith(self.branch_prefix) and pr.user.id == self.con.user.id

    def matches_current_version(self, pr: PullRequest) -> bool:
        """Check if `pr` is a template update PR for the current version"""
        return pr.head.ref == self.branch and pr.user.id == self.con.user.id


class RepoInfo(TypedDict):
    """Info about a repository using the cookiecutter-scverse template"""

    url: str
    skip: NotRequired[bool]


def get_template_release(gh: Github, tag_name: str) -> GHRelease:
    """
    Get a release by tag from the cookiecutter-scverse repo

    `gh` represents the github API, authenticated against scverse-bot.
    """
    template_repo = gh.get_repo("scverse/cookiecutter-scverse")
    return template_repo.get_release(tag_name)


def _parse_repos(f: IO[str] | str) -> list[RepoInfo]:
    repos = cast("list[RepoInfo]", safe_load(f))
    log.info(f"Found {len(repos)} known repos")
    return repos


def get_repo_urls(gh: Github) -> Generator[str]:
    """
    Get a list of all repos using the cookiecutter-scverse template (based on a YML file in scverse/ecosystem-packages)

    `gh` represents the github API, authenticated against scverse-bot.
    """
    repo = gh.get_repo("scverse/ecosystem-packages")
    file = cast("ContentFile", repo.get_contents("template-repos.yml"))
    for repo in _parse_repos(file.decoded_content):
        if not repo.get("skip"):
            yield repo["url"]


def run_cruft(cwd: Path, *, tag_name: str, log_name: str) -> CompletedProcess:
    args = [
        sys.executable,
        "-m",
        "cruft",
        "update",
        f"--checkout={tag_name}",
        "--skip-apply-ask",
        "--project-dir=.",
    ]

    log_path = Path(f"./log/{log_name}.txt")
    log_path.parent.mkdir(exist_ok=True)

    with log_path.open("w") as log_file:
        return run(args, check=True, cwd=cwd, stdout=log_file, stderr=log_file)


def template_update(con: GitHubConnection, *, repo: GHRepo) -> bool:
    """
    Create or update a template branch in the forked repo

    Parameters
    ----------
    con
        A connection to the github API, authenticated against scverse-bot
    repo

    """
    pass
    clone = retry_with_backoff(
        lambda: Repo.clone_from(con.auth(repo.clone_url), path), retries=n_retries, exc_cls=GitCommandError
    )


def cruft_update(  # noqa: PLR0913
    con: GitHubConnection,
    pr: PR,
    *,
    tag_name: str,
    repo: GHRepo,
    origin: GHRepo,
    path: Path,
) -> bool:
    clone = retry_with_backoff(
        lambda: Repo.clone_from(con.auth(repo.clone_url), path),
        retries=n_retries,
        exc_cls=GitCommandError,
    )
    upstream = clone.create_remote(name=pr.repo_id, url=origin.clone_url)
    upstream.fetch()
    branch = clone.create_head(pr.branch, f"{pr.repo_id}/{origin.default_branch}")
    branch.checkout()

    run_cruft(path, tag_name=tag_name, log_name=pr.branch)

    if not clone.is_dirty():
        return False

    # Stage & Commit
    # Maybe clean? changed_files = [diff.b_path or diff.a_path for diff in cast(list[Diff], clone.index.diff(None))]
    # and then: clone.index.add([*clone.untracked_files, changed_files])
    clone.git.add(all=True)
    commit = clone.index.commit(pr.title, parent_commits=[branch.commit], author=con.sig, committer=con.sig)
    branch.commit = commit

    # Push
    remote = clone.remote()
    remote.set_url(con.auth(repo.clone_url))
    remote.push([branch.name])
    return True


def get_fork(con: GitHubConnection, repo: GHRepo) -> GHRepo:
    """
    Fork target repo into the scverse-bot namespace and wait until the fork has been created.

    If the fork already exists, it is reused.

    Parameters
    ----------
    con
        Github API connection, authenticated against scverse-bot
    repo
        Reference to the *original* github repo that uses the template (i.e. not the fork)
    """
    log.info(f"Creating fork for {repo.url}")
    fork = repo.create_fork()
    return retry_with_backoff(
        lambda: con.gh.get_repo(fork.id),
        retries=n_retries,
        exc_cls=UnknownObjectException,
    )


def make_pr(con: GitHubConnection, release: GHRelease, repo_url: str) -> None:
    repo_id = repo_url.replace("https://github.com/", "").replace("/", "-")
    pr = PR(con, release, repo_id)
    log.info(f"Sending PR to {repo_url} : {pr.title}")

    # create fork, populate branch, do PR from it
    original_repo = con.gh.get_repo(repo_url.removeprefix("https://github.com/"))
    forked_repo = get_fork(con, original_repo)

    if old_pr := next((p for p in original_repo.get_pulls("open") if pr.matches_current_version(p)), None):
        log.info(
            f"PR for current version already exists: #{old_pr.number} with branch name `{old_pr.head.ref}`. Skipping."
        )
        return

    with TemporaryDirectory() as td:
        updated = cruft_update(
            con,
            pr,
            tag_name=release.tag_name,
            repo=forked_repo,
            origin=original_repo,
            path=Path(td),
        )
    if updated:
        if old_pr := next((p for p in original_repo.get_pulls("open") if pr.matches_prefix(p)), None):
            log.info(f"Closing old PR #{old_pr.number} with branch name `{old_pr.head.ref}`.")
            old_pr.edit(state="closed")
        new_pr = original_repo.create_pull(
            title=pr.title,
            body=pr.body,
            base=original_repo.default_branch,
            head=pr.namespaced_head,
            maintainer_can_modify=True,
        )
        log.info(f"Created PR #{new_pr.number} with branch name `{new_pr.head.ref}`.")


cli = App()


@cli.default
def main(tag_name: str, repo_urls: list[str] | None = None, *, all_repos: bool = False) -> None:
    """
    Make PRs to github repos.

    Parameters
    ----------
    tag_name
        Identifier of the release of cookiecutter-scverse
    repo_urls
        One or more repo URLs to make PRs to (e.g. for testing purposes).
        Must be full github URLs, e.g. https://github.com/scverse/scirpy.
    all
        With this flag, get the list of all repos that use the template from https://github.com/scverse/ecosystem-packages/blob/main/template-repos.yml.
    """
    setup_logging()

    token = os.environ["GITHUB_TOKEN"]
    con = GitHubConnection("scverse-bot", token)

    if all_repos:
        repo_urls = get_repo_urls(con.gh)

    if repo_urls is None:
        msg = "Need to either specify `--all` or one or more repo URLs."
        raise ValueError(msg)

    release = get_template_release(con.gh, tag_name)
    failed = 0
    for repo_url in repo_urls:
        try:
            make_pr(con, release, repo_url)
        except Exception as e:
            failed += 1
            log.exception(f"Error updating {repo_url}: %s", e)

    sys.exit(failed > 0)


if __name__ == "__main__":
    cli()
