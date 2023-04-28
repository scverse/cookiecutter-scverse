"""Script to send cruft update PRs.

Uses `template-repos.yml` from `scverse/ecosystem-packages`.
"""

import os
from collections.abc import Generator
from dataclasses import dataclass, field
from logging import basicConfig, getLogger
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from typing import IO, NotRequired, TypedDict, cast
from urllib.parse import urlparse

import typer
from git.repo import Repo
from git.util import Actor
from github import Github
from github.ContentFile import ContentFile
from github.GitRelease import GitRelease as GHRelease
from github.Repository import Repository as GHRepo
from yaml import safe_load

log = getLogger(__name__)


@dataclass
class GitHubConnection:
    name: str
    email: str
    token: str = field(repr=False)
    gh: Github = field(init=False)
    sig: Actor = field(init=False)

    def __post_init__(self) -> None:
        self.gh = Github(self.token)
        self.sig = Actor(self.name, self.email)

    def auth(self, url_str: str) -> str:
        url = urlparse(url_str)
        # TODO: not mutable
        url.username = self.name
        url.password = self.token
        return url


@dataclass
class PR:
    release: GHRelease

    @property
    def title(self) -> str:
        return f"Update template to {self.release.tag_name}"

    @property
    def branch(self) -> str:
        return f"template-update-{self.release.tag_name}"

    @property
    def body(self) -> str:
        template_usage = "https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html"
        return f"""\
`cookiecutter-scverse` released [{self.release.title}]({self.release.html_url}).

## Changes

{self.release.body}

## Additional remarks
* unsubscribe: If you don`t want to receive these PRs in the future,
  add `skip: true` to [`template-repos.yml`][] using a PR or,
  if you never want to sync from the template again, delete your `.cruft` file.
* If there are **merge conflicts**,
  they either show up inline (`>>>>>>>`) or a `.rej` file will have been created for the respective files.
  You need to address these conflicts manually. Make sure to enable pre-commit.ci (see below) to detect such files.
* The scverse template works best when the [pre-commit.ci][], [readthedocs][] and [codecov][] services are enabled.
  Make sure to activate those apps if you haven't already.

[template-repos.yml]: https://github.com/scverse/ecosystem-packages/blob/main/template-repos.yml
[pre-commit.ci]: {template_usage}#pre-commit-ci
[readthedocs]: {template_usage}#documentation-on-readthedocs
[codecov]: {template_usage}#coverage-tests-with-codecov
"""


class RepoInfo(TypedDict):
    url: str
    skip: NotRequired[bool]


def get_template_release(gh: Github, tag_name: str) -> GHRelease:
    template_repo = gh.get_repo("scverse/cookiecutter-scverse")
    return template_repo.get_release(tag_name)


def parse_repos(f: IO[str] | str) -> list[RepoInfo]:
    repos = cast(list[RepoInfo], safe_load(f))
    log.info(f"Found {len(repos)} known repos")
    return repos


def get_repo_urls(gh: Github) -> Generator[str]:
    repo = gh.get_repo("scverse/ecosystem-packages")
    file = cast(ContentFile, repo.get_contents("template-repos.yml"))
    for repo in parse_repos(file.decoded_content):
        if not repo.get("skip"):
            yield repo["url"]


def cruft_update(con: GitHubConnection, repo: GHRepo, path: Path, pr: PR) -> bool:
    clone = Repo.clone_from(con.auth(repo.git_url), path)
    branch = clone.create_head(pr.branch)
    branch.checkout()

    args = ["cruft", "update", " --checkout=main", "--skip-apply-ask", "--project-dir=."]
    run(args, check=True)

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


def make_pr(con: GitHubConnection, release: GHRelease, repo_url: str) -> None:
    pr = PR(release)
    log.info(f"Sending PR to {repo_url}: {pr.title}")

    # create fork, populate branch, do PR from it
    origin = con.gh.get_repo(repo_url.removeprefix("https://github.com/"))
    repo = origin.create_fork()
    with TemporaryDirectory() as td:
        updated = cruft_update(con, repo, Path(td), pr)
    if updated:
        origin.create_pull(pr.title, pr.body, ...)  # TODO


def setup() -> None:
    from rich.logging import RichHandler
    from rich.traceback import install

    basicConfig(level="INFO", handlers=[RichHandler()])
    install(show_locals=True)


def main(tag_name: str) -> None:
    token = os.environ["GITHUB_TOKEN"]
    con = GitHubConnection("scverse-bot", "core-team@scverse.org", token)
    release = get_template_release(con.gh, tag_name)
    repo_urls = get_repo_urls(con.gh)
    for repo_url in repo_urls:
        make_pr(con, release, repo_url)


def cli() -> None:
    typer.run(main)


if __name__ == "__main__":
    cli()