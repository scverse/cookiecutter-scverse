"""Notify downstream repositories that a new template version is available.

Replaces the old PR-sending bot (``cruft_prs.py``). Instead of forking every repo
and pushing a (frequently conflict-ridden) template-update branch, this opens a
single tracking **issue** per repo pointing at the ``scverse-template-update`` agent
skill. A maintainer then assigns the coding agent of their choice to the issue, and
the agent performs the update — preserving intentional deviations rather than
producing mechanical merge conflicts.

The list of repos comes from ``template-repos.yml`` in ``scverse/ecosystem-packages``.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Iterable
from typing import TYPE_CHECKING, TypedDict, cast

from cyclopts import App
from github import Auth, Github
from yaml import safe_load

from ._log import log, setup_logging

if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import NotRequired

    from github.ContentFile import ContentFile
    from github.GitRelease import GitRelease as GHRelease
    from github.Issue import Issue
    from github.NamedUser import NamedUser
    from github.Repository import Repository

# Hidden marker embedded in every issue body so we can find (and update) the issue we
# previously opened, without relying on the title (which maintainers may rename).
MARKER_PREFIX = "<!-- scverse-template-update:"


def issue_marker(tag: str) -> str:
    return f"{MARKER_PREFIX}{tag} -->"


def parse_issue_tag(body: str | None) -> str | None:
    """Extract the template tag a bot issue was last written for, if any."""
    if not body or MARKER_PREFIX not in body:
        return None
    rest = body.split(MARKER_PREFIX, 1)[1]
    return rest.split("-->", 1)[0].strip() or None


def issue_title(tag: str) -> str:
    return f"Template update available: {tag}"


ISSUE_BODY_TEMPLATE = """\
A new release of the [`cookiecutter-scverse`]({template_url}) template — \
[**{tag}**]({release_url}) — is available, and your repository is built from it.
Updating keeps your CI, build system, and developer tooling in line with current
scverse best practices.

## What's new in {tag}

{release_body}

## How to apply this update

This update is meant to be carried out by an **AI coding agent** of your choice
(e.g. the Claude GitHub app, or any agent you run against a local checkout). The
template ships a skill that does the heavy lifting: it re-renders the template at
your repo's recorded version and at {tag}, works out which files you changed *on
purpose* versus which are merely *stale*, and applies the modernization while
keeping your intentional customizations — no blind merge conflicts.

1. **Assign your coding agent to this issue** (or open a clean checkout locally).
2. **Point it at the skill** and ask it to update this repository to {tag}:
   - Instructions: [`SKILL.md`]({skill_md_url})
   - Helper script: [`sync_helper.py`]({helper_url})

   A one-line prompt that works for most agents:
   > Update this repository to `cookiecutter-scverse` {tag} by following the
   > instructions at {skill_md_url} (use `--repo .` and `--tag {tag}`). Open a PR
   > that closes this issue.
3. **Review the PR** the agent opens. It will summarize what it modernized, which
   of your deviations it preserved (and why), and anything it left for your review.

### Prefer to do it by hand?

You can still update manually with cruft: ensure a clean working tree, then run
`cruft update`. See the template-usage docs for details.

## Remarks

* **Unsubscribe**: add `skip: true` to [`template-repos.yml`][repos] via PR, or — to
  stop syncing from the template entirely — delete `.cruft.json` from your repo root.
* The template works best with [pre-commit.ci][], [readthedocs][] and [codecov][]
  enabled; make sure those apps are activated.

[repos]: https://github.com/scverse/ecosystem-packages/blob/main/template-repos.yml
[pre-commit.ci]: https://pre-commit.ci/
[readthedocs]: https://readthedocs.org/
[codecov]: https://about.codecov.io/

{marker}
"""


def skill_urls(template_slug: str, tag: str) -> tuple[str, str]:
    """(human-readable SKILL.md URL, raw sync_helper.py URL) pinned to the release tag."""
    base = ".claude/skills/scverse-template-update"
    skill_md = f"https://github.com/{template_slug}/blob/{tag}/{base}/SKILL.md"
    helper = f"https://raw.githubusercontent.com/{template_slug}/{tag}/{base}/sync_helper.py"
    return skill_md, helper


def render_issue_body(*, tag: str, release: GHRelease, template_url: str, template_slug: str) -> str:
    skill_md_url, helper_url = skill_urls(template_slug, tag)
    return ISSUE_BODY_TEMPLATE.format(
        tag=tag,
        release_url=release.html_url,
        release_body=(release.body or "").strip() or "_See the release notes linked above._",
        template_url=template_url,
        skill_md_url=skill_md_url,
        helper_url=helper_url,
        marker=issue_marker(tag),
    )


class RepoInfo(TypedDict):
    """Info about a repository using the cookiecutter-scverse template."""

    url: str
    skip: NotRequired[bool]


def _parse_repos(f: str | bytes) -> list[RepoInfo]:
    repos = cast("list[RepoInfo]", safe_load(f))
    log.info(f"Found {len(repos)} known repos")
    return repos


def get_repo_urls(gh: Github) -> Generator[str]:
    """Yield the URLs of all (non-skipped) repos that use the template."""
    repo = gh.get_repo("scverse/ecosystem-packages")
    file = cast("ContentFile", repo.get_contents("template-repos.yml"))
    for entry in _parse_repos(file.decoded_content):
        if not entry.get("skip"):
            yield entry["url"]


def get_template_release(gh: Github, template_slug: str, tag_name: str) -> GHRelease:
    return gh.get_repo(template_slug).get_release(tag_name)


def is_bot_template_issue(issue: Issue, bot_user_id: int) -> bool:
    """An open issue we previously opened (matched by hidden marker + author)."""
    return issue.pull_request is None and MARKER_PREFIX in (issue.body or "") and issue.user.id == bot_user_id


def notify_repo(repo: Repository, bot: NamedUser, *, tag: str, body: str, dry_run: bool) -> None:
    """Create or update the single tracking issue in `repo`.

    Idempotent: if an open bot issue already targets `tag`, do nothing; if one targets
    an older tag, edit it in place; otherwise create a new one. Closed issues are left
    untouched (the maintainer already dealt with them).
    """
    title = issue_title(tag)

    existing = [i for i in repo.get_issues(state="open", creator=bot.login) if is_bot_template_issue(i, bot.id)]

    if up_to_date := [i for i in existing if parse_issue_tag(i.body) == tag]:
        log.info(f"{repo.full_name}: issue #{up_to_date[0].number} already targets {tag}, skipping")
        return

    if existing:
        issue = existing[0]
        if len(existing) > 1:
            log.warning(f"{repo.full_name}: {len(existing)} open template issues; updating #{issue.number} only")
        if dry_run:
            log.info(f"{repo.full_name}: would update issue #{issue.number} -> {tag}")
            return
        issue.edit(title=title, body=body)
        log.info(f"{repo.full_name}: updated issue #{issue.number} -> {tag}")
        return

    if dry_run:
        log.info(f"{repo.full_name}: would create issue '{title}'")
        return
    new_issue = repo.create_issue(title=title, body=body)
    log.info(f"{repo.full_name}: created issue #{new_issue.number}")


cli = App()


@cli.default
def main(
    tag_name: str,
    repo_urls: Iterable[str] | None = None,
    *,
    all_repos: bool = False,
    dry_run: bool = False,
    template_url: str = "https://github.com/scverse/cookiecutter-scverse",
) -> None:
    """Open/refresh a template-update notification issue in downstream repos.

    Parameters
    ----------
    tag_name
        Release tag of cookiecutter-scverse to notify about.
    repo_urls
        One or more full repo URLs to notify (e.g. for testing).
    all_repos
        Notify every repo listed in scverse/ecosystem-packages/template-repos.yml.
    dry_run
        Log intended actions without creating or editing any issues.
    template_url
        URL of the template repo (used for the release/skill links).
    """
    setup_logging()
    template_slug = template_url.removeprefix("https://github.com/").rstrip("/")

    gh = Github(auth=Auth.Token(os.environ["GITHUB_TOKEN"]))
    bot = cast("NamedUser", gh.get_user())  # the authenticated bot account

    if all_repos:
        repo_urls = list(get_repo_urls(gh))
    if not repo_urls:
        msg = "Need to either pass `--all-repos` or one or more repo URLs."
        raise ValueError(msg)

    release = get_template_release(gh, template_slug, tag_name)
    body = render_issue_body(tag=tag_name, release=release, template_url=template_url, template_slug=template_slug)

    failed = 0
    for repo_url in repo_urls:
        try:
            repo = gh.get_repo(repo_url.removeprefix("https://github.com/").rstrip("/"))
            notify_repo(repo, bot, tag=tag_name, body=body, dry_run=dry_run)
        except Exception as e:  # one bad repo shouldn't abort the rest
            failed += 1
            log.error(f"Failed to notify {repo_url}")
            log.exception(e)

    sys.exit(failed > 0)


if __name__ == "__main__":
    cli()
