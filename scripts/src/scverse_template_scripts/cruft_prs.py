"""Script to send cruft update PRs.

Uses `template-repos.yml` from `scverse/ecosystem-packages`.
"""

from __future__ import annotations

import json
import math
import os
import sys
from dataclasses import InitVar, dataclass, field
from pathlib import Path  # noqa
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
    email: str = field(default=None)

    def __post_init__(self, login: str) -> None:
        self.gh = Github(self.token)
        self.user = self.gh.get_user(login)
        if self.email is None:
            self.email = self.user.email
        self.sig = Actor(self.login, self.email)

    @property
    def login(self) -> str:
        return self.user.login

    def auth(self, url_str: str) -> str:
        url = furl(url_str)
        if self.token:
            url.username = self.token
        return str(url)


@dataclass
class TemplateUpdatePR:
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


def template_update(
    con: GitHubConnection,
    *,
    forked_repo: GHRepo,
    original_repo: GHRepo,
    workdir: Path,
    tag_name: str,
    cruft_log_file: Path,
) -> bool:
    """
    Create or update a template branch in the forked repo

    This is a replacement for `cruft update` that implements all the template update logic from
    scratch. This is done because using this function, conflicts will show up as actual merge
    conflicts on github, rather than creating `.rej` files.

    Here's a rough description of the approach:
    1) fork the repo to update into the scverse-bot namespace
    2) If no `template-update` branch exists in the fork, create one from the initial commit of the repo
    3) check out the `template-update` branch
    3) Remove everything from the template-branch.
    4) Use `cruft create` to instantiate the template into a separate directory
    5) sync the changes from the separate directory into the `template-branch`
    6) commit

    --> From this commit, we can make a pull-request to the original repo including the latest template-changes.

    Parameters
    ----------
    con
        A connection to the github API, authenticated against scverse-bot
    forked_repo
        The repo forked in scverse-bot namespace
    original_repo
        The original (upstream) repo
    workdir
        A (temporary) path that is used as a working directory to clone and update the repo
    tag_name
        tag name of cookiecutter template to use
    cruft_log_file
        Filename to write cruft logs to

    """
    # Clone the repo with blob filtering for better performance
    clone_dir = workdir / "clone"
    log.info(f"Cloning {forked_repo.clone_url} into {clone_dir}")
    clone = retry_with_backoff(
        lambda: Repo.clone_from(con.auth(forked_repo.clone_url), clone_dir, filter="blob:none"),
        retries=n_retries,
        exc_cls=GitCommandError,
    )

    # Add original repo as remote
    upstream = clone.create_remote(name="upstream", url=original_repo.clone_url)
    upstream.fetch()

    # Get the default branch
    default_branch = original_repo.default_branch

    # Get cruft config from the default branch in the upstream repo
    log.info(f"Getting .cruft.json from the {default_branch} in {original_repo.clone_url}")
    try:
        # Try to get .cruft.json from the latest commit in upstream's default branch
        cruft_content = clone.git.show(f"upstream/{default_branch}:.cruft.json")
        cruft_config = json.loads(cruft_content)
        log.info(f"Successfully read .cruft.json from upstream/{default_branch}")
    except GitCommandError:
        msg = "No .cruft.json found in repository"
        raise FileNotFoundError(msg) from None

    # Check if the branch already exists in the forked repo
    remote_refs = [ref.name for ref in clone.remote().refs]
    branch_name = "scverse-bot/template-update"
    full_branch_name = f"refs/heads/{branch_name}"

    # create and/or checkout template-update branch
    if full_branch_name not in remote_refs:
        log.info(f"Branch {branch_name} does not exists yet, creating it from initial commit")
        # Get the initial commit on the default branch
        initial_commit = next(clone.iter_commits(default_branch, reverse=True))

        # Create and checkout a new branch from the initial commit
        branch = clone.create_head(branch_name, initial_commit)
        branch.checkout()
    else:
        log.info(f"Branch {branch_name} already exists, checking it out")
        branch = clone.create_head(branch_name, f"origin/{branch_name}")
        branch.checkout()

    # Remove everything from the repo (except the `.git` directoroy)
    cmd = ["/usr/bin/find", ".", "-not", "-path", "./.git*", "-delete"]
    log.info("Running " + " ".join(cmd) + " in ", clone_dir)
    run(cmd, check=True, cwd=clone_dir)

    # Initalize a new repo off the current template version, using the configuration from .cruft.json
    template_dir = workdir / "template"
    cookiecutter_config = template_dir / "cookiecutter.json"
    with cookiecutter_config.open("w") as f:
        # need to put the cookiecutter-related info from .cruft.json into separate file
        json.dump(cruft_config["context"]["cookiecutter"], f)
    # run in a subprocess, otherwise not possible to catpure output of post-run hooks
    with cruft_log_file.open("w") as log_f:
        cmd = [
            sys.executable,
            "-m",
            "cruft",
            "create",
            "https://github.com/scverse/cookiecutter-scverse",
            f"--checkout={tag_name}",
            "--no-input",
            f"--extra-context-file={cookiecutter_config}",
        ]
        log.info("Running " + " ".join(cmd))
        run(
            cmd,
            stdout=log_f,
            stderr=log_f,
            check=True,
            cwd=template_dir,
        )
    template_dir = template_dir / cruft_config["context"]["cookiecutter"]["project_name"]

    # move over the contents from the new directory into the emptied git repo
    cmd = ["/usr/bin/rsync", "-Pva", "--exclude", ".git", f"{template_dir}/", f"{clone_dir}/"]
    log.info("Running " + " ".join(cmd) + " in ", workdir)
    run(cmd, check=True, cwd=workdir, capture_output=True)

    # Check if something has changed at all
    if not clone.is_dirty():
        log.info("Nothing has changed, aborting")
        return False

    # Stage and commit (no_verify to don't run pre-commit)
    log.info("Changes detected. Staging and committing changes.")
    clone.git.add(A=True)
    clone.git.commit(
        m=f"Automated template update to {tag_name}",
        no_verify=True,
        author=f"{con.sig.name} <{con.sig.email}>",
        no_gpg_sign=True,
    )

    # Push
    log.info(f"Pushing changes to {forked_repo.clone_url}")
    remote = clone.remote()
    remote.set_url(con.auth(forked_repo.clone_url))
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


def make_pr(con: GitHubConnection, release: GHRelease, repo_url: str, *, log_dir: Path, dry_run: bool = False) -> None:
    """
    Make a pull request with the template update to the original repo

    Parameters
    ----------
    con
        A connection to the github API, authenticated against scverse-bot
    release
        A github release object, pointing to the release of cookiecutter-scverse to be used
    repo_url
        git URL of the repo to update
    log_dir
        Path in which cruft logs will be stored
    dry_run
        If True, skip making the actual pull request but perform all other actions up to this point

    """
    repo_id = repo_url.replace("https://github.com/", "").replace("/", "-")
    log.info(f"Working on template update for {repo_id}")

    pr = TemplateUpdatePR(con, release, repo_id)
    # create fork, populate branch, do PR from it
    original_repo = con.gh.get_repo(repo_url.removeprefix("https://github.com/"))
    if old_pr := next((p for p in original_repo.get_pulls("open") if pr.matches_current_version(p)), None):
        log.info(
            f"PR for current version already exists: #{old_pr.number} with branch name `{old_pr.head.ref}`. Skipping."
        )
        return

    forked_repo = get_fork(con, original_repo)

    with TemporaryDirectory() as td:
        updated = template_update(
            con,
            forked_repo=forked_repo,
            original_repo=original_repo,
            workdir=td,
            tag_name=release.tag_name,
            cruft_log_file=log_dir / f"{pr.branch}.log",
        )
    if updated:
        if old_pr := next((p for p in original_repo.get_pulls("open") if pr.matches_prefix(p)), None):
            log.info(f"Closing old PR #{old_pr.number} with branch name `{old_pr.head.ref}`.")
            old_pr.edit(state="closed")
        if dry_run:
            log.info("Skipping PR because in dry-run mode")
            return
        log.info(f"Creating PR of {pr.namespace_heat} against {original_repo.default_branch}")
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
def main(
    tag_name: str,
    repo_urls: list[str] | None = None,
    *,
    all_repos: bool = False,
    log_dir: Path = "cruft_logs",
    dry_run: bool = False,
) -> None:
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
    log_dir
        Directory to which cruft logs are written
    dry_run
        Skip making actual pull requests. All other actions up to this point are performed
        (forking the repo, updating the template branch etc.).
    """
    setup_logging()

    token = os.environ["GITHUB_TOKEN"]
    con = GitHubConnection("scverse-bot", token, email="108668866+scverse-bot@users.noreply.github.com")

    if all_repos:
        repo_urls = get_repo_urls(con.gh)

    if repo_urls is None:
        msg = "Need to either specify `--all` or one or more repo URLs."
        raise ValueError(msg)

    release = get_template_release(con.gh, tag_name)
    failed = 0
    for repo_url in repo_urls:
        try:
            make_pr(con, release, repo_url, log_dir=log_dir, dry_run=dry_run)
        except Exception as e:
            failed += 1
            log.exception(f"Error updating {repo_url}: %s", e)

    sys.exit(failed > 0)


if __name__ == "__main__":
    cli()
