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
from github.GitRelease import GitRelease
from yaml import safe_load

log = getLogger(__name__)


class Repo(TypedDict):
    url: str
    skip: NotRequired[bool]


def get_template_release(gh: Github, tag_name: str) -> GitRelease:
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


def make_pr(gh: Github, release: GitRelease, repo_url: str) -> None:
    log.info(f"Sending PR to {repo_url}")

    # TODO
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
    print(gh, release, repo_url, title, body)


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
