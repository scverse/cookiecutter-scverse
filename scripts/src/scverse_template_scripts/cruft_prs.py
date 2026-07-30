"""Script to send cruft update PRs.

Uses `template-repos.yml` from `scverse/ecosystem-packages`.
"""

from __future__ import annotations

import contextlib
import json
import math
import os
import re
import sys
from collections.abc import Iterable
from dataclasses import KW_ONLY, InitVar, dataclass, field
from glob import glob
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, ClassVar, TypedDict, cast

from cyclopts import App
from furl import furl
from git.exc import GitCommandError
from git.repo import Repo
from git.util import Actor
from github import Auth, Github, UnknownObjectException
from yaml import safe_load

from ._log import log, setup_logging
from .backoff import retry_with_backoff

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence
    from typing import IO, Literal, LiteralString, NotRequired

    from github.ContentFile import ContentFile
    from github.GitRelease import GitRelease as GHRelease
    from github.NamedUser import NamedUser
    from github.PullRequest import PullRequest
    from github.Repository import Repository as GHRepo


PR_BODY_TEMPLATE = """\
`cookiecutter-scverse` released [{release.tag_name}]({release.html_url}).

{release.body}

## Additional remarks
* **unsubscribe**: If you don’t want to receive these PRs in the future,
  add `skip: true` to [`template-repos.yml`][] using a PR or,
  if you never want to sync from the template again, delete the `.cruft.json` file in the root of your repository.
* If there are **merge conflicts**, you can resolve them manually, or let an AI coding
  agent do it for you: assign a coding agent (e.g. GitHub Copilot) to this PR and point
  it at the [conflict-resolution skill][] with a prompt like *"Resolve the merge conflicts
  in this PR by following {skill_url}"*. The skill adopts the template's updates while
  preserving the deviations your project made on purpose. You can also run it locally with
  Claude Code.
* The scverse template works best when the [pre-commit.ci][], [readthedocs][] and [codecov][] services are enabled.
  Make sure to activate those apps if you haven't already.
* If you have questions on the template sync, feel free to tag @grst or reach out on scverse.zulipchat.com.

[`template-repos.yml`]: https://github.com/scverse/ecosystem-packages/blob/main/template-repos.yml
[conflict-resolution skill]: {skill_url}
[pre-commit.ci]: {template_usage}#pre-commit-ci
[readthedocs]: {template_usage}#documentation-on-readthedocs
[codecov]: {template_usage}#coverage-tests-with-codecov
"""

# GitHub says that up to 5 minutes of waiting for a fork are OK,
# So we error our once we wait longer, i.e. when 2ⁿ = 5 min × 60 sec/min
N_RETRIES_WAIT_FOR_FORK = math.ceil(math.log(5 * 60) / math.log(2))  # = ⌈~8.22⌉ = 9
# Due to exponential backoff, we’ll maximally wait 2⁹ sec, or 8.5 min

# For the following variables, always use the template version
# (remove them from the cookiecutter context provided by the instance during update)
COOKIECUTTER_VARS_OVERRIDE_FROM_TEMPLATE = ["_copy_without_render", "_exclude_on_template_update"]


def _escape_github_mentions(text: str) -> str:
    """Escape GitHub @mentions with backticks to prevent notifications.

    Wraps ``@username`` patterns in backticks so that GitHub doesn't treat them as
    real mentions when the release notes are embedded in template-update PRs.
    Otherwise every contributor named in the release notes would be subscribed to
    the ~150 template-update PRs that are opened on every release.

    Already-escaped mentions and email addresses are left unchanged.

    Note
    ----
    This is a simple regex that comes with certain limitations,
    e.g., a mention that sits *inside* an inline code span but is preceded by whitespace
    (e.g.  ``\\`see @bar here\\```) would be re-escaped incorrectly.
    This does not occur in GitHub's auto-generated release notes (a flat bullet list of `… by @user in <url>`).

    At the time of writing, we couldn't identify a library providing a markdown parser
    that reliably identifies github usernames.
    """
    # A GitHub @mention, e.g. `@grst`. The username pattern matches GitHub's own rules:
    # alphanumeric or single non-leading/non-trailing/non-consecutive hyphens, max 39 chars.
    # See https://github.com/shinnn/github-username-regex.
    # The negative lookbehind skips email addresses (e.g. `bot@example.com`) and
    # already-escaped mentions (e.g. `` `@grst` ``).
    github_username_regex = re.compile(
        r"(?<![`\w])@([a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38})",
        re.IGNORECASE,
    )

    return github_username_regex.sub(r"`@\1`", text)


@dataclass
class GitHubConnection:
    """API connection to a GitHub user (e.g. scverse-bot)"""

    _login: InitVar[str]
    token: str | None = field(repr=False, default=None)
    _: KW_ONLY
    email: str | None = field(default=None)

    gh: Github = field(init=False)
    user: NamedUser = field(init=False)
    sig: Actor = field(init=False)

    def __post_init__(self, _login: str) -> None:
        self.gh = Github(auth=Auth.Token(self.token) if self.token else None)
        self.user = cast("NamedUser", self.gh.get_user(_login))
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
class TemplateRelease:
    """A cookiecutter-scverse release, together with the exact commit it was tagged at.

    `GHRelease` does not expose the commit sha directly, so we resolve and cache it here.
    """

    release: GHRelease
    commit: str
    template_url: str

    @property
    def tag_name(self) -> str:
        return self.release.tag_name

    @property
    def html_url(self) -> str:
        return self.release.html_url

    @property
    def body(self) -> str:
        return self.release.body


@dataclass
class TemplateUpdatePR:
    """A template update pull request to a repository using the cookiecutter-scverse template"""

    con: GitHubConnection
    release: TemplateRelease
    repo_id: str  # something like scverse-scirpy

    title_prefix: ClassVar[LiteralString] = "Update template to "
    # -v2 to distinguish from branch names generated from earlier version of template sync that was using cruft
    # (before v0.5.0 release of cookiecutter-scverse)
    branch_prefix: ClassVar[LiteralString] = "template-update-v2-"

    @property
    def title(self) -> str:
        return f"{self.title_prefix}{self.release.tag_name}"

    @property
    def template_branch(self) -> str:
        """Branch name in the forked repo that tracks template updates (stay the same across versions)"""
        # as of v0.5.0 (new template sync), the branch name does not contain the release-tag anymore
        return f"{self.branch_prefix}{self.repo_id}"

    @property
    def pr_branch(self) -> str:
        """Name of the branch that is used to create the pull-request. A new branch is created for each version."""
        return f"{self.template_branch}-{self.release.tag_name}"

    @property
    def namespaced_head(self) -> str:
        """Branch used to crate the pull request, including repo namespace"""
        return f"{self.con.login}:{self.pr_branch}"

    @property
    def body(self) -> str:
        body = PR_BODY_TEMPLATE.format(
            release=self.release,
            template_usage="https://cookiecutter-scverse-instance.readthedocs.io/page/template_usage.html",
            skill_url=(
                "https://github.com/scverse/cookiecutter-scverse/blob/"
                f"{self.release.tag_name}"
                "/.claude/skills/scverse-template-resolve-conflicts/SKILL.md"
            ),
        )
        return _escape_github_mentions(body)

    def matches_prefix(self, pr: PullRequest) -> bool:
        """Check if `pr` is either a current or previous template update PR by matching the branch name"""
        # Don’t compare title prefix, people might rename PRs
        return pr.head.ref.startswith(self.branch_prefix) and pr.user.id == self.con.user.id

    def matches_current_version(self, pr: PullRequest) -> bool:
        """Check if `pr` is a template update PR for the current version"""
        return pr.head.ref == self.pr_branch and pr.user.id == self.con.user.id


class RepoInfo(TypedDict):
    """Info about a repository using the cookiecutter-scverse template"""

    url: str
    skip: NotRequired[bool]


def get_template_release(gh: Github, template_url: str, tag_name: str) -> TemplateRelease:
    """
    Get a release by tag from the template repo, alongside the commit it points to.

    `gh` represents the github API, authenticated against scverse-bot.
    """
    template_repo = gh.get_repo(template_url.removeprefix("https://github.com/"))
    release = template_repo.get_release(tag_name)
    commit = template_repo.get_commit(tag_name).sha
    return TemplateRelease(release=release, template_url=template_url, commit=commit)


def _parse_repos(f: IO[str] | str | bytes) -> list[RepoInfo]:
    repos = cast("list[RepoInfo]", safe_load(f))
    log.info(f"Found {len(repos)} known repos")
    return repos


def get_repo_urls(gh: Github) -> Generator[str]:
    """
    Get a list of all repos using the cookiecutter-scverse template (based on a YML file in scverse/ecosystem-packages).

    `gh` represents the github API, authenticated against scverse-bot.
    """
    repo = gh.get_repo("scverse/ecosystem-packages")
    file = cast("ContentFile", repo.get_contents("template-repos.yml"))
    for repo in _parse_repos(file.decoded_content):
        if not repo.get("skip"):
            yield repo["url"]


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
        retries=N_RETRIES_WAIT_FOR_FORK,
        exc_cls=UnknownObjectException,
    )


def _clone_and_prepare_repo(
    con: GitHubConnection, clone_dir: Path, template_branch_name: str, *, forked_repo: GHRepo, original_repo: GHRepo
) -> Repo:
    """
    Clone the forked repo and set up branches and remotes.

    This function
     * clones the forked repo
     * adds the original repo as a remote named "upstream"
     * checks out a branch called `{template_branch_name}`. If it does not exist yet,
       it is created off the initial commit of the default branch of the original repo.

    Parameters
    ----------
    con
        GitHub connection
    clone_dir
        directory into which to clone the repo
    forked_repo
        reference to the forked repo (to be cloned)
    original_repo
        reference to the original repo (to be set as upstream)
    template_branch_name
        branch to contain the repo template (to be added to fork)
    """
    # Clone the repo with blob filtering for better performance
    log.info(f"Cloning {forked_repo.clone_url} into {clone_dir}")
    clone = retry_with_backoff(
        lambda: Repo.clone_from(con.auth(forked_repo.clone_url), clone_dir, filter="blob:none"),
        retries=N_RETRIES_WAIT_FOR_FORK,
        exc_cls=GitCommandError,
    )

    # Add original repo as remote
    upstream = clone.create_remote(name="upstream", url=original_repo.clone_url)
    upstream.fetch()

    # Get the default branch
    default_branch = original_repo.default_branch

    # Check if the branch already exists in the forked repo
    remote_refs = [ref.name for ref in clone.remote("origin").refs]
    full_branch_name = f"origin/{template_branch_name}"

    # create and/or checkout template-update branch
    if full_branch_name not in remote_refs:
        log.info(f"Branch {template_branch_name} does not exists yet, creating it from initial commit")
        # Get the initial commit on the default branch
        initial_commit = next(clone.iter_commits(default_branch, reverse=True))

        # Create and checkout a new branch from the initial commit
        branch = clone.create_head(template_branch_name, initial_commit.hexsha)
        branch.checkout()
    else:
        log.info(f"Branch {template_branch_name} already exists, checking it out")
        branch = clone.create_head(template_branch_name, full_branch_name)
        branch.checkout()

    return clone


class CruftConfig(TypedDict):
    context: dict[Literal["cookiecutter"], dict[str, str]]


def _get_cruft_config_from_upstream(repo: Repo, default_branch: str) -> CruftConfig:
    """Get cruft config from the default branch in the upstream repo"""
    log.info(f"Getting .cruft.json from the {default_branch} branch in {repo.remote('upstream').url}")
    try:
        # Try to get .cruft.json from the latest commit in upstream's default branch
        cruft_content = repo.git.show(f"upstream/{default_branch}:.cruft.json")
        cruft_config = cast("CruftConfig", json.loads(cruft_content))
        log.info(f"Successfully read .cruft.json from upstream/{default_branch}")
    except GitCommandError:
        msg = "No .cruft.json found in repository"
        raise FileNotFoundError(msg) from None

    return cruft_config


def _apply_update(
    clone: Repo,
    *,
    cruft_log_file: Path,
    cookiecutter_config: dict,
    template_dir: str,
) -> None:
    """
    Apply the changes from the template to the target repo.

    Instantiate the cookiecutter template with the config used by the target repo.
    Then remove everything from the target repo and copy over all template files.

    The outcome is a branch in the target repo that contains the updated template that can be merged
    into the default branch by the user.

    Parameters
    ----------
    clone
        cloned target repository (to which the update is to be applied)
    cruft_log_file
        file to which the cruft log will be written
    cookiecutter_config
        cookiecutter configuration to be passed to cruft as `--extra-context-file`
    template_dir
        path to the template (cloned git repository, already checked out at the desired tag)
    """
    clone_dir = Path(clone.working_dir)
    with TemporaryDirectory() as td:
        output_dir = Path(td)
        # Initialize a new repo off the current template version, using the configuration from .cruft.json
        cookiecutter_config_file = output_dir / "cookiecutter.json"
        with cookiecutter_config_file.open("w") as f:
            # need to put the cookiecutter-related info from .cruft.json into separate file
            json.dump(
                {k: v for k, v in cookiecutter_config.items() if k not in COOKIECUTTER_VARS_OVERRIDE_FROM_TEMPLATE}, f
            )

        # run in a subprocess, otherwise not possible to capture output of post-run hooks
        with cruft_log_file.open("w") as log_f:
            # Do not specify --checkout to point to a specific tag.
            # The correct version is already checked out in `template_dir`
            cmd = [
                sys.executable,
                "-m",
                "cruft",
                "create",
                template_dir,
                "--no-input",
                f"--extra-context-file={cookiecutter_config_file}",
            ]
            log.info("Running " + " ".join(cmd))
            run(cmd, stdout=log_f, stderr=log_f, check=True, cwd=output_dir)
        template_dir_project_name = output_dir / cookiecutter_config["project_name"]

        # Remove everything from the original repo (except the `.git` directoroy)
        cmd = ["/usr/bin/find", ".", "-not", "-path", "./.git*", "-delete"]
        log.info("Running " + " ".join(cmd) + f" in {clone_dir}")
        run(cmd, check=True, cwd=clone_dir)

        # move over the contents from the new directory into the emptied git repo
        cmd = [
            "/usr/bin/rsync",
            "-Pva",
            "--exclude",
            ".git",
            f"{template_dir_project_name.absolute()}/",
            f"{clone_dir.absolute()}/",
        ]
        log.info("Running " + " ".join(repr(a) if " " in a else a for a in cmd))
        run(cmd, check=True, capture_output=True)


def _commit_update(clone: Repo, *, exclude_files: Sequence = (), commit_msg: str, commit_author: str) -> bool:
    """
    Check if changes were made, and if yes, commit them.

    Glob patterns in `exclude_files` will not be staged for the commit.

    Returns a `bool` indicating whether changes have been made and committed.
    """
    # Stage and commit (no_verify to avoid running the git hooks)
    log.info("Changes detected. Staging and committing changes.")
    # Check if something has changed at all
    if not clone.is_dirty() and not clone.untracked_files:
        log.info("Nothing has changed, aborting")
        return False

    clone.git.add(A=True)
    # unstage the files that we want to exclude from the template update
    log.info(f"Excluding files from patterns: {exclude_files}")
    for glob_pattern in exclude_files:
        # need to check if pattern matches anything, because
        if len(glob(glob_pattern, root_dir=clone.working_dir)):
            clone.git.restore(glob_pattern, staged=True)

    # Check if there are any staged changes for commit
    if not clone.git.diff_index("HEAD", cached=True, name_only=True):
        log.info("Nothing has changed after excluding files, aborting")
        return False

    clone.git.commit(m=commit_msg, no_verify=True, author=commit_author, no_gpg_sign=True)
    return True


def template_update(
    con: GitHubConnection,
    *,
    forked_repo: GHRepo,
    original_repo: GHRepo,
    template_branch_name: str,
    versioned_branch_name: str,
    release: TemplateRelease,
    cruft_log_file: Path,
    dry_run: bool,
    template_dir: str,
) -> bool:
    """
    Create or update a template branch in the forked repo.

    Replacement for `cruft update` that implements all the template update logic from scratch.
    Using this function, conflicts will show up as actual merge conflicts on Github, rather than creating `.rej` files.

    Here's a rough description of the approach:
    1) fork the repo to update into the scverse-bot namespace
    2) If no `template-update` branch exists in the fork, create one from the initial commit of the repo
    3) check out the `template-update` branch
    3) Remove everything from the template-branch
    4) Use `cruft create` to instantiate the template into a separate directory
    5) sync the changes from the separate directory into the `template-branch`
    6) commit
    7) check out commit into a version-specific branch used for making the pull request. See #396 for why this is
       necessary.

    --> From this commit, we can make a pull-request to the original repo including the latest template-changes.

    Parameters
    ----------
    con
        A connection to the github API, authenticated against scverse-bot
    forked_repo
        The repo forked in scverse-bot namespace
    template_branch_name
        branch name to use for the template in the forked repo
    versioned_branch_name
        version-specific branch name (will be created off the template branch)
    original_repo
        The original (upstream) repo
    release
        The release of cookiecutter-scverse to use, together with the commit it points to
    cruft_log_file
        Filename to write cruft logs to
    dry_run
        If True, do not push changes

    """
    with (
        TemporaryDirectory() as clone_dir_str,
        _clone_and_prepare_repo(
            con,
            (clone_dir := Path(clone_dir_str)),
            template_branch_name,
            forked_repo=forked_repo,
            original_repo=original_repo,
        ) as clone,
    ):
        default_branch: str = original_repo.default_branch

        cruft_config = _get_cruft_config_from_upstream(clone, default_branch)
        cookiecutter_config = cruft_config["context"]["cookiecutter"]
        _apply_update(
            clone,
            cruft_log_file=cruft_log_file,
            cookiecutter_config=cookiecutter_config,
            template_dir=template_dir,
        )

        # Load .cruft.json file of the current version of the template (includes `_exclude_on_template_update` key)
        with (clone_dir / ".cruft.json").open() as f:
            tmp_config = json.load(f)
            exclude_files = tmp_config["context"]["cookiecutter"].get("_exclude_on_template_update", [])

        # Update .cruft.json with current tag and commit hash.
        # This is necessary since we don't run `cruft create` with `--checkout`
        # and `template_dir` contains the correct version with an additional patch-commit (see `download_template`).
        tmp_config["commit"] = release.commit
        tmp_config["checkout"] = release.tag_name
        tmp_config["template"] = release.template_url
        tmp_config["context"]["_commit"] = release.commit
        tmp_config["context"]["_template"] = release.template_url
        with (clone_dir / ".cruft.json").open("w") as f:
            json.dump(tmp_config, f, indent=2)

        if (
            updated := _commit_update(
                clone,
                exclude_files=exclude_files,
                commit_msg=f"Automated template update to {release.tag_name}",
                commit_author=f"{con.sig.name} <{con.sig.email}>",
            )
        ) and not dry_run:
            clone.git.switch(versioned_branch_name, template_branch_name, C=True)
            clone.git.push("origin", template_branch_name)
            clone.git.push("origin", versioned_branch_name)

        return updated


def make_pr(
    con: GitHubConnection,
    release: TemplateRelease,
    repo_url: str,
    *,
    log_dir: Path,
    dry_run: bool = False,
    template_dir: str,
) -> None:
    """
    Make a pull request with the template update to the original repo

    Parameters
    ----------
    con
        A connection to the github API, authenticated against scverse-bot
    release
        The release of cookiecutter-scverse to be used, together with the commit it points to
    repo_url
        git URL of the repo to update
    log_dir
        Path in which cruft logs will be stored
    dry_run
        If True, skip making the actual pull request but perform all other actions up to this point
    template_dir
        path to the git repository with the cookiecutter template
    """
    repo_id = repo_url.replace("https://github.com/", "").replace("/", "-")
    log.info(f"Working on template update for {repo_id}")

    pr = TemplateUpdatePR(con, release, repo_id)
    # create fork, populate branch, do PR from it
    original_repo = con.gh.get_repo(repo_url.removeprefix("https://github.com/"))

    forked_repo = get_fork(con, original_repo)

    template_update(
        con,
        forked_repo=forked_repo,
        original_repo=original_repo,
        template_branch_name=pr.template_branch,
        versioned_branch_name=pr.pr_branch,
        release=release,
        cruft_log_file=log_dir / f"{pr.template_branch}.log",
        dry_run=dry_run,
        template_dir=template_dir,
    )
    if dry_run:
        log.info("Skipping PR because in dry-run mode")
        return

    # check against all PRs, including closed ones -- if one already exists for the current version,
    # and the developer closed it, we do not want to reopen it.
    if old_pr := next((p for p in original_repo.get_pulls("all") if pr.matches_current_version(p)), None):
        log.info(f"PR already exists: #{old_pr.number} with branch name `{old_pr.head.ref}`. Skipping PR creation.")
        return

    # check if there's a PR open for an earlier version -- if yes, we close it (in favor of the new one to be created)
    if old_pr := next((p for p in original_repo.get_pulls("open") if pr.matches_prefix(p)), None):
        log.info(f"Closing old PR #{old_pr.number} with branch name `{old_pr.head.ref}`.")
        old_pr.edit(state="closed")

    log.info(f"Creating PR of {pr.namespaced_head} against {original_repo.default_branch}")
    new_pr = original_repo.create_pull(
        title=pr.title,
        body=pr.body,
        base=original_repo.default_branch,
        head=pr.namespaced_head,
        maintainer_can_modify=True,
    )
    log.info(f"Created PR #{new_pr.number} with branch name `{new_pr.head.ref}`.")


cli = App()


@contextlib.contextmanager
def download_template(con: GitHubConnection, template_url: str, tag_name: str) -> Generator[str, None, None]:
    """
    Clone the template repository into a temporary directory and check out a tag name.

    This avoids repeated downloads of the template.

    Patches cookiecutter.json config, such that lists are replaced with empty strings.
    This avoids issues with template sync in cases users specified options that are outside the (currently)
    allowed cateogories specified in the cookiecutter.json (https://github.com/scverse/cookiecutter-scverse/issues/460).

    Parameters
    ----------
    con
        GitHub connection used to authenticate the clone URL
    template_url
        URL of the template repository to clone

    Yields
    ------
    str
        Path to the temporary directory containing the cloned repository
    """
    with TemporaryDirectory() as td:
        clone = Repo.clone_from(con.auth(template_url), td, filter="blob:none")
        clone.git.checkout(tag_name)
        with (Path(td) / "cookiecutter.json").open() as f:
            cookiecutter_config = json.load(f)

        # Replace list values with an empty string to allow arbitrary values passed in via --extra-context-file,
        # but keep those lists that are to be taken from the template
        cookiecutter_config_patched = {
            k: "" if isinstance(v, list) and k not in COOKIECUTTER_VARS_OVERRIDE_FROM_TEMPLATE else v
            for k, v in cookiecutter_config.items()
        }
        with (Path(td) / "cookiecutter.json").open("w") as f:
            json.dump(cookiecutter_config_patched, f)

        clone.git.add("cookiecutter.json")
        clone.git.commit(message="Patch cookiecutter.json")

        yield td


@cli.default
def main(
    tag_name: str,
    repo_urls: Iterable[str] | None = None,
    *,
    all_repos: bool = False,
    log_dir: Path = Path("cruft_logs"),
    dry_run: bool = False,
    template_url: str = "https://github.com/scverse/cookiecutter-scverse",
) -> None:
    """
    Make PRs to GitHub repos.

    Parameters
    ----------
    tag_name
        Identifier of the release of cookiecutter-scverse
    repo_urls
        One or more repo URLs to make PRs to (e.g. for testing purposes).
        Must be full GitHub URLs, e.g. https://github.com/scverse/scirpy.
    all
        With this flag, get the list of all repos that use the template from https://github.com/scverse/ecosystem-packages/blob/main/template-repos.yml.
    log_dir
        Directory to which cruft logs are written
    dry_run
        Skip making actual pull requests. All other actions up to this point are performed
        (forking the repo, updating the template branch etc.).
    """
    setup_logging()
    log_dir.mkdir(exist_ok=True, parents=True)

    token = os.environ["GITHUB_TOKEN"]
    con = GitHubConnection("scverse-bot", token, email="108668866+scverse-bot@users.noreply.github.com")

    if all_repos:
        repo_urls = get_repo_urls(con.gh)

    if repo_urls is None:
        msg = "Need to either specify `--all` or one or more repo URLs."
        raise ValueError(msg)

    release = get_template_release(con.gh, template_url, tag_name)
    failed = 0
    with download_template(con, template_url, tag_name) as template_dir:
        for repo_url in repo_urls:
            try:
                make_pr(
                    con,
                    release,
                    repo_url,
                    log_dir=log_dir,
                    dry_run=dry_run,
                    template_dir=template_dir,
                )
            except Exception as e:
                failed += 1
                log.error(f"Error while updating {repo_url}")
                log.exception(e)

    sys.exit(failed > 0)


if __name__ == "__main__":
    cli()
