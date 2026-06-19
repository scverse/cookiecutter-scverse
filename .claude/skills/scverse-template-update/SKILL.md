---
name: scverse-template-update
description: Update a downstream repository to a new release of the cookiecutter-scverse template, intelligently preserving deviations the project made on purpose while still modernizing CI, build system, and tool versions. Use when asked to sync/update an scverse ecosystem package to a new template tag — an agent-driven replacement for the programmatic cruft-based sync that avoids tedious merge conflicts.
---

# scverse-template-update

Sync a repository built from **cookiecutter-scverse** up to a newer template release.

On a new template release, the scverse bot opens a tracking issue in each downstream
repo (`scripts/src/scverse_template_scripts/template_issues.py`) and a maintainer
assigns an agent to it — that's where you come in. This replaces the old PR-sending
bot, which did a blind 3-way merge: it re-rendered the template and forced every
change onto the repo, so any file the project changed on purpose came back as a
merge conflict the maintainer had to resolve by hand. **Your advantage is
judgement.** You can read the project's
git history to tell an *intentional* customization apart from a file that is merely
*stale*, propagate the template's modernizations cleanly, and only escalate the
genuinely ambiguous cases to a human.

## Inputs

- **Target repo** — a local path, or a GitHub `owner/repo` / URL to clone first.
  If you were **assigned to a GitHub issue** asking for this update, the target is
  the current checkout (`--repo .`).
- **New template tag** — e.g. `v0.6.0`. A git tag in the cookiecutter-scverse repo.
  When triggered from an issue, the tag is stated in the issue body/title.
- **Template source** (optional) — defaults to the `template` URL recorded in the
  repo's `.cruft.json`. Override with a local checkout when validating an
  unreleased tag (e.g. point at the current working tree of this template repo).

If any of these is missing or ambiguous, ask before proceeding.

### Getting this skill's helper script

Downstream repos don't ship the skill — it lives in the cookiecutter-scverse repo.
If `.claude/skills/scverse-template-update/sync_helper.py` is **not** already present
in your checkout, download it (pinned to the tag you're updating to) before step 2:

```bash
mkdir -p .tmpl-sync
curl -fsSL -o .tmpl-sync/sync_helper.py \
  "https://raw.githubusercontent.com/scverse/cookiecutter-scverse/<tag>/.claude/skills/scverse-template-update/sync_helper.py"
```

and run that copy in place of the path shown in step 2. (If you are reading these
very instructions from a URL rather than a local `SKILL.md`, fetch the helper the
same way.)

## How the sync works conceptually

The repo's `.cruft.json` records (a) the template URL, (b) the `commit` it was last
synced to, and (c) the exact cookiecutter answers (`context.cookiecutter`). With
those answers we render the template **twice** — at the old commit and at the new
tag — using the project's own values. Then for every file we know three things:
its old-template version (`T_old`), its new-template version (`T_new`), and the
repo's current version (`R`). That cross-tabulation drives every decision:

| Situation | Meaning | Default action |
|---|---|---|
| `T_old == T_new` | template didn't touch this file | leave `R` untouched |
| file only in `T_new` | template added a file | add it (reconcile if `R` already differs) |
| file only in `T_old` | template removed a file | remove from repo (confirm it isn't repurposed) |
| `T_old != T_new`, `R == T_old` | template changed it, repo never customized | **take `T_new` verbatim** (clean modernization) |
| `T_old != T_new`, `R != T_old` | template changed it **and** repo diverged | **judgement call** — 3-way merge (below) |
| file only in repo | project content (`src/`, `tests/`, …) | never touch |

`sync_helper.py` computes all of this for you. You spend your effort only on the
"judgement call" row.

## Procedure

### 1. Prepare

- Ensure the target repo is checked out and its working tree is **clean**
  (`git -C <repo> status`). Refuse to run on a dirty tree.
- Never work on the default branch. Create `git switch -c template-update-<tag>`.
- Confirm `.cruft.json` exists. If it doesn't, this repo isn't template-linked —
  stop and tell the user (the legacy `cruft update` path doesn't apply either).

### 2. Run the helper

```bash
python .claude/skills/scverse-template-update/sync_helper.py \
    --repo <repo> --tag <tag> [--template <path-or-url>] --workdir <scratch>
```

It renders `render_old/` and `render_new/`, and writes `manifest.json`. Read the
manifest. It also surfaces the skip lists:
- `_exclude_on_template_update` (from `.cruft.json`) and
- `[tool.cruft] skip` in the repo's `pyproject.toml`
These mark **user-owned** files (`src/**`, `tests/**`, `README.md`, `CHANGELOG.md`,
`docs/api.md`, `docs/index.md`, the example notebook, references, package
`__init__.py`/`basic.py`). Do not overwrite their *content*; only make a minimal
edit if a template change strictly requires it, and call it out.

### 3. Apply the clean changes (no judgement needed)

- **`template_modified_repo_clean`**: copy `render_new/<path>` over the repo file.
- **`template_added`**: add `render_new/<path>`. If the repo already has a
  differing version, treat it like a diverged file (step 4).
- **`template_removed`**: remove from the repo, unless the file was clearly
  repurposed for project use (check `git log`) — when unsure, leave it and note it.
- **`template_unchanged`** / **`repo_only_files`**: leave alone.

### 4. Reconcile the diverged files (the point of this skill)

For each entry in `template_modified_repo_diverged`, the manifest includes the
`template_diff` — the `T_old → T_new` change, i.e. *what the new template wants*.
For each one:

1. **Understand the divergence.** Why does `R` differ from `T_old`?
   ```bash
   git -C <repo> log --oneline --follow -- <path>
   git -C <repo> log -p --follow -- <path>      # read the actual commits
   ```
   - If the only commits touching it are past **template-sync / cruft** commits, or
     the content simply matches an *older* template, the divergence is **stale** →
     take `T_new` verbatim.
   - If a deliberate, project-specific commit changed it (extra CI job, different
     Python version matrix, added dependency, custom RTD/codecov config, tweaked
     ruff rules, …), the divergence is **intentional** → preserve it.

2. **3-way merge for intentional divergence.** Start from the repo's file `R` and
   apply *only* the hunks of `template_diff` that are orthogonal to the
   customization. Concretely: take the template's modernization (bumped action
   versions, new build-backend settings, renamed keys, added steps) **and** keep
   the project's intentional content. The goal is "repo's intent + template's
   freshness," never a `<<<<<<<` conflict marker left in a file.

3. **When genuinely unclear**, prefer preserving the project's version and record
   the file in a "needs human review" list for the PR body rather than guessing.

### 5. Modernization mandate

Regardless of divergence, the repo **must** end up modern on infrastructure unless
a clear intentional customization says otherwise. Pay special attention to:

- `.github/workflows/**` — runner images, action versions (`actions/checkout`,
  `setup-uv`, …), permissions blocks, job structure.
- `.pre-commit-config.yaml` — hook repos and `rev:` pins.
- `pyproject.toml` — `[build-system]`, hatch envs, `requires-python`, classifiers,
  ruff/tool config, dependency-group layout.
- `.readthedocs.yaml`, `docs/conf.py` machinery, `.codecov.yaml`, `.editorconfig`.

If you preserved an *old* tool version because the repo pinned it, double-check the
pin was intentional (a comment or a commit explaining why) — otherwise modernize it.

### 6. Finalize

1. **Update `.cruft.json`**: set `"commit"` to the new template commit
   (`new_commit` in the manifest) and bump any recorded checkout/tag. Keep
   `context.cookiecutter` unchanged unless the template added new variables — if so,
   add them with the template's defaults and note it.
2. **Verify** in the repo (best effort; report what passes/fails, don't hide
   failures):
   ```bash
   cd <repo>
   git add -A
   pre-commit run --all-files            # or: prek run --all-files
   uv run python -c "import <package_name>"
   hatch run docs:build                  # if docs deps install cleanly
   ```
   Fix mechanical fallout you introduced (formatting, an import the template moved).
   Do not paper over a real failure caused by an intentional-divergence decision —
   surface it.
3. **Commit** on the `template-update-<tag>` branch with a message like
   `Update template to <tag>`.
4. **Open a PR** (only if the user asked, or you have a clear remote + auth). If you
   were assigned to a template-update **issue**, the PR should close it (add
   `Closes #<issue-number>` to the body). The PR body should make the maintainer's
   review easy:
   - what was modernized (CI, build, tool bumps),
   - which deviations were **preserved** and why (cite the commits/reasons),
   - anything **left for human review** and why,
   - a reminder that pre-commit.ci / readthedocs / codecov should be enabled.

## Guardrails

- Read before you overwrite. A file matching `_exclude_on_template_update` or
  `[tool.cruft] skip` is the project's, not the template's.
- Prefer a smaller, correct diff over a sweeping one. The maintainer should be able
  to understand every change you made and why.
- Never leave conflict markers, `.rej`, or `.orig` files behind.
- When you couldn't decide, say so explicitly — an honest "needs review" beats a
  confident wrong merge.
