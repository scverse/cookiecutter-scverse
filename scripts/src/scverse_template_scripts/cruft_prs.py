"""Script to send cruft update PRs.

Uses `template-repos.yml` from `scverse/ecosystem-packages`.
"""

import os
from collections.abc import Generator
from logging import basicConfig, getLogger
from typing import IO, NotRequired, TypedDict, cast

import typer
from github import Github
from github.ContentFile import ContentFile
from github.GitRelease import GitRelease as GHRelease
from github.Repository import Repository as GHRepo
from pygit2 import RemoteCallbacks, Signature, UserPass, clone_repository
from yaml import safe_load

log = getLogger(__name__)


class Repo(TypedDict):
    url: str
    skip: NotRequired[bool]


def get_template_release(gh: Github, tag_name: str) -> GHRelease:
    template_repo = gh.get_repo("scverse/cookiecutter-scverse")
    return template_repo.get_release(tag_name)


def parse_repos(f: IO[str] | str) -> list[Repo]:
    repos = cast(list[Repo], safe_load(f))
    log.info(f"Found {len(repos)} known repos")
    return repos


def get_repo_urls(gh: Github) -> Generator[str]:
    repo = gh.get_repo("scverse/ecosystem-packages")
    file = cast(ContentFile, repo.get_contents("template-repos.yml"))
    for repo in parse_repos(file.decoded_content):
        if not repo.get("skip"):
            yield repo["url"]


def cruft_update(token: str, repo: GHRepo):
    author = committer = Signature("scverse-bot", "core-team@scverse.org")
    callbacks = RemoteCallbacks(UserPass(author.name, token))

    # TODO: path, contents, commit msg, cruft exec, …

    # Clone the newly created repo
    clone = clone_repository(repo.git_url, "/path/to/clone/to", callbacks=callbacks)

    # put the files in the repository here

    # Commit it
    clone.remotes.set_url("origin", repo.clone_url)
    index = clone.index
    index.add_all()
    index.write()
    tree = index.write_tree()
    clone.create_commit("refs/heads/master", author, committer, "init commit", tree, [clone.head.get_object().hex])
    remote = clone.remotes["origin"]
    # remote.credentials = UserPass...

    remote.push(["refs/heads/master"], callbacks=callbacks)


def create_pr_data(release: GHRelease) -> tuple[str, str]:
    template_usage = "https://cookiecutter-scverse-instance.readthedocs.io/en/latest/template_usage.html"
    title = f"Update template to {release.tag_name}"
    body = f"""\
`cookiecutter-scverse` released [{release.title}]({release.html_url}).

## Changes

{release.body}

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

    return title, body


def make_pr(gh: Github, release: GHRelease, repo_url: str) -> None:
    title, body = create_pr_data(release)
    log.info(f"Sending PR to {repo_url}: {title}")

    # create fork, populate branch, do PR from it
    origin = gh.get_repo(repo_url.removeprefix("https://github.com/"))
    repo = origin.create_fork()
    cruft_update(repo)
    origin.create_pull(title, body, ...)  # TODO


def setup() -> None:
    from rich.logging import RichHandler
    from rich.traceback import install

    basicConfig(level="INFO", handlers=[RichHandler()])
    install(show_locals=True)


def main(tag_name: str) -> None:
    gh = Github(os.environ["GITHUB_TOKEN"])
    release = get_template_release(gh, tag_name)
    repo_urls = get_repo_urls(gh)
    for repo_url in repo_urls:
        make_pr(gh, release, repo_url)


def cli() -> None:
    typer.run(main)


if __name__ == "__main__":
    cli()
