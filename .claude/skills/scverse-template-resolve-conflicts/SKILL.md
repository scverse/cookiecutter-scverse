---
name: scverse-template-resolve-conflicts
description: Resolve the merge conflicts in a cookiecutter-scverse "Update template to vX.X.X" pull request. The scverse bot opens these PRs on every template release; they conflict wherever the downstream repo customized a template-managed file. Use to adopt the template's modernizations (CI, build system, tool/action versions, docs boilerplate) while preserving the project's deliberate deviations — resolving what you confidently can and handing the rest to a human.
---

# scverse-template-resolve-conflicts

Resolve conflicts in a **cookiecutter-scverse template-update pull request**.

On every template release, the scverse bot
(`scripts/src/scverse_template_scripts/cruft_prs.py`) opens an "Update template to
`<tag>`" PR in each downstream repo. The PR's head branch is a **fresh render of the
new template**, rooted at the repo's *initial commit*, so GitHub 3-way-merges it
against the project's current default branch. Every template-managed file the project
changed on purpose (`pyproject.toml`, `.pre-commit-config.yaml`, workflows,
`.gitignore`, `.editorconfig`, …) shows up as a **merge conflict**.

Your job: bring the repo up to the new template — modern CI, build system, tool and
action versions, docs/contributing boilerplate — **while preserving the deviations the
project made deliberately**. Your advantage over the old programmatic merge is
**judgement**: you can read git history to tell an *intentional* customization apart
from a merely *stale* file, and you can escalate only the genuinely ambiguous cases.

## Inputs

- **The PR** — a number or URL (e.g. `#183` / `https://github.com/OWNER/REPO/pull/183`),
  or "the current PR" if you're already on its checkout. If you can't tell which PR,
  ask.
- **Conflict-handling mode** — how to treat conflicts you *cannot* confidently resolve.
  The right default depends on **how you were invoked**:
  - **`leave-markers`** — *default when a human runs you locally.* Resolve the files
    you're confident about and **leave standard `<<<<<<<` conflict markers** in the
    uncertain ones, so the maintainer can finish them in their IDE. The template ships a
    `check-merge-conflict` pre-commit hook, so pre-commit.ci / CI will fail and block the
    merge until the markers are resolved.
  - **`resolve-and-flag`** — *default when you were assigned to the PR as a remote /
    online coding agent* (e.g. GitHub Copilot), with no human at a terminal. Resolve
    every file; when unsure, keep the **repo's** version and add the file to a "please
    review" list posted as a PR comment. The PR stays mergeable.

  If the user stated a mode, honor it. Otherwise pick the default that matches your
  invocation context: a human running you locally → `leave-markers`; a remote assignment
  on the PR → `resolve-and-flag`.

This skill needs only `git` and the `gh` CLI — nothing from the downstream repo. If you
are an assigned coding agent reading this from a URL, you can run it as-is.

## Mental model

You resolve the PR by **merging the base branch into the PR head branch** and reconciling
each conflict, then pushing. After that merge the head contains the base, so GitHub sees
the PR as mergeable.

Turn on `zdiff3` conflict markers first (`git config merge.conflictstyle zdiff3`). Each
conflict then shows **three** regions, and the mapping is:

```
<<<<<<< HEAD
    ...the NEW TEMPLATE's version (what we want to adopt)...
||||||| merged common ancestor
    ...the COMMON ANCESTOR (≈ the original template render — what both sides started from)...
=======
    ...the REPO's CURRENT version (the project's customizations)...
>>>>>>> origin/<base>
```

> Note the direction: because you merge *base into head*, `HEAD` is the **template** and
> `origin/<base>` is the **repo**. Don't blindly take `--ours`/`--theirs`.

**Resolution rule:** compute the template's change (`ancestor → HEAD`) and apply it on
top of the **repo's** version (`origin/<base>`). Adopt the template's modernization; keep
the project's deliberate content; drop only content that is stale (an older template that
the new one supersedes and the project never customized).

## Procedure

### 1. Prepare

```bash
gh pr view <pr> --json number,headRefName,baseRefName,headRepositoryOwner
gh pr checkout <pr>                      # checks out the PR head branch (handles forks)
git status                               # must be clean; refuse to run on a dirty tree
base=$(gh pr view <pr> --json baseRefName -q .baseRefName)
git fetch origin "$base"
git config merge.conflictstyle zdiff3    # local to this repo; better 3-way markers
```

### 2. Materialize the conflicts

```bash
git merge --no-edit "origin/$base"
```

Files that exist only in the repo (`src/**`, `tests/**`, notebooks, …) merge in
automatically — the PR branch simply didn't have them. Conflicts land only on the
template-managed files both sides touched.

```bash
git diff --name-only --diff-filter=U      # the files you must resolve
```

### 3. Learn the skip lists (user-owned files)

Two lists mark files the project *owns* — for these, **prefer the repo's version** and
only take a template change if it's strictly required (and say so):

- `_exclude_on_template_update` in `.cruft.json` (e.g. `README.md`, `CHANGELOG.md`,
  `LICENSE`, `docs/api.md`, `docs/index.md`, `docs/references.*`, the example notebook,
  `src/**`, `tests/**`).
- `[tool.cruft] skip` in the repo's `pyproject.toml`.

```bash
git show "origin/$base:.cruft.json" 2>/dev/null | grep -A20 _exclude_on_template_update
git show "origin/$base:pyproject.toml" 2>/dev/null | grep -A20 '\[tool.cruft\]'
```

### 4. Resolve each conflicted file

For every file from step 2:

1. **Read all three sides** from the `zdiff3` markers. Ask: what did the template change
   (`ancestor → HEAD`)? What did the repo change (`ancestor → repo`)? Do they overlap?

2. **Judge intentional vs. stale** using history on the repo side:
   ```bash
   git log --oneline origin/$base -- <path>
   git log -p origin/$base -- <path>        # read the commits that changed it
   git blame origin/$base -- <path>
   ```
   - Only past **template-sync / cruft / bot** commits, or content that just matches an
     *older* template → **stale** → take the template's version (`HEAD`).
   - A deliberate project commit (extra CI job, different Python matrix, added
     dependency, custom RTD/codecov config, tweaked ruff rules, …) → **intentional** →
     keep it, and still layer in the template's orthogonal modernizations.

3. **Write the reconciled file**: repo's intent **+** template's freshness. Remove all
   conflict markers for files you resolve. File-type guidance:
   - **`.cruft.json`** — take the new template `commit` (the value on `HEAD`), but keep
     the repo's `context.cookiecutter` answers.
   - **`.github/workflows/**`** — adopt new runner images, pinned action hashes/versions,
     `permissions:` blocks, and job structure; keep any project-specific jobs/matrix.
   - **`.pre-commit-config.yaml`** — adopt the template's new hook repos and `rev:` pins;
     keep project-added hooks.
   - **`pyproject.toml`** — adopt `[build-system]`, hatch envs, ruff/tool config,
     classifiers, `requires-python`; **keep the project's real dependencies** and any
     intentional tool settings.
   - **`.gitignore` / `.editorconfig`** — usually a clean union; take template additions,
     keep project-specific entries.

4. **Confidence handling** — decide per file:
   - Confident → write the reconciled content and `git add <path>`.
   - Not confident:
     - **`resolve-and-flag`** (default): keep the **repo's** version (safest), `git add`
       it, and record the path for the review comment.
     - **`leave-markers`**: leave the `<<<<<<<` markers in place and `git add` the file
       as-is (do **not** strip the markers).

### 5. Complete the merge

- **`resolve-and-flag`**: let hooks run and fix mechanical fallout (formatting, a moved
  import):
  ```bash
  git commit --no-edit
  ```
- **`leave-markers`**: the `check-merge-conflict` hook would (correctly) reject the
  markers, so bypass it for this merge commit:
  ```bash
  git commit --no-edit --no-verify
  ```

### 6. Verify (best effort — report, don't hide failures)

```bash
pre-commit run --all-files        # or: prek run --all-files
uv run python -c "import <package_name>"
hatch run docs:build              # if docs deps install cleanly
```

Fix fallout you introduced. Do **not** paper over a real failure caused by a resolution
decision — surface it. In `leave-markers` mode, `check-merge-conflict` failing on the
files you intentionally left is expected.

### 7. Push and report

```bash
git push
```

The bot opens its PRs with `maintainer_can_modify = true`, so a maintainer's checkout can
push to the head branch; an assigned agent pushes to the fork it has access to.

Then comment on the PR (`gh pr comment <pr> --body ...`) summarizing, so the maintainer's
review is quick:

- **Modernized**: what you adopted from the template (CI, build, tool/action bumps).
- **Preserved**: which deviations you kept and why (cite the commits/reasons).
- **Needs human review** (`resolve-and-flag`) / **Left as conflicts** (`leave-markers`):
  the exact files, and what's ambiguous about each.
- A reminder that pre-commit.ci / readthedocs / codecov should be enabled for the repo.

## Guardrails

- Read before you overwrite. A file matching `_exclude_on_template_update` or
  `[tool.cruft] skip` belongs to the project, not the template.
- Mind the merge direction: `HEAD` = template, `origin/<base>` = repo. Never resolve by a
  blanket `--ours`/`--theirs`.
- Prefer a smaller, correct diff over a sweeping one. The maintainer should be able to
  understand every change and why.
- In `resolve-and-flag` mode, leave **no** stray conflict markers. In `leave-markers`
  mode, leave markers **only** in files you genuinely couldn't resolve.
- Never leave `.rej` or `.orig` files behind.
- When you couldn't decide, say so explicitly — an honest "needs review" beats a
  confident wrong merge.
