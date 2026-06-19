# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is **not** a Python package — it is a [cookiecutter](https://github.com/cookiecutter/cookiecutter) template used (via [cruft](https://github.com/cruft/cruft)) to scaffold new [scverse](https://scverse.org) ecosystem packages. The generated projects are best-practice Python libraries that depend on `anndata`/`mudata`.

Two distinct concerns live side by side:

1. **The template itself** — everything under `{{cookiecutter.project_name}}/`, controlled by `cookiecutter.json` and the `hooks/` scripts. Files here are Jinja2 templates rendered at generation time.
2. **`scripts/`** — a real, installable Python package (`scverse-template-scripts`) containing automation that runs in CI, most importantly the bot that sends template-update PRs to downstream repos.

## Key architectural points

### Template rendering (`{{cookiecutter.project_name}}/`)
- Files are rendered with Jinja2. `cookiecutter.json` defines the variables (`project_name`, `package_name`, `license`, `ide_integration`, `issue_categorization`, plus `_`-prefixed config).
- `_jinja2_env_vars` sets `trim_blocks`/`lstrip_blocks`, so `{% %}` block lines don't leave blank lines.
- `_copy_without_render` lists files copied verbatim (e.g. downstream GitHub workflows that themselves contain `{{ }}` syntax). Editing those requires no Jinja escaping.
- `_exclude_on_template_update` lists files cruft won't overwrite when updating an existing project (user-owned files like `src/**`, `tests/**`, `README.md`).
- **Conditional files/dirs**: a path like `{{".vscode" if cookiecutter.ide_integration else "DELETE-ME"}}/` renders to a directory literally named `DELETE-ME` when disabled; `hooks/post_gen_project.py` then deletes every `DELETE-ME` directory after generation.
- `hooks/post_gen_project.py` also makes the initial git commit (so cruft has a clean template-only baseline) and installs pre-commit. `hooks/pre_gen_project.py` runs validation before rendering.

### Template-update notifier (`scripts/src/scverse_template_scripts/template_issues.py`)
- Entry point `send-template-issues` (`scripts.send-template-issues` in `scripts/pyproject.toml`). Triggered by `.github/workflows/template-issues.yml` on a GitHub **release** (not pre-release).
- Reads the list of downstream repos from `template-repos.yml` in `scverse/ecosystem-packages`, then opens (or refreshes) one tracking **issue** per repo announcing the new tag. The issue links the `scverse-template-update` agent skill (by URL, pinned to the tag); a maintainer assigns a coding agent to perform the update. Repos opt out via `skip: true` there or by deleting `.cruft.json`.
- Idempotent via a hidden `<!-- scverse-template-update:<tag> -->` marker: an open bot issue already at the tag is skipped, one at an older tag is edited in place, closed issues are left alone.
- This **replaced** the previous PR-based bot (`cruft_prs.py`), which forked/cloned/re-rendered each repo and pushed a template-update branch — that produced tedious merge conflicts on intentionally-customized files. The agent-driven flow reconciles semantically instead. The actual update logic lives in the skill at `.claude/skills/scverse-template-update/` (`SKILL.md` + `sync_helper.py`), not in `scripts/`.

## Commands

All Python tooling uses `uv`/`hatch`. There is no top-level Python package to install.

### Working on `scripts/`
```bash
cd scripts
uvx hatch test                 # run the test suite
uvx hatch test -- -k test_name # run a single test
```
Note: `test_build.py` runs cookiecutter against the template and asserts on rendered output and that no `DELETE-ME` dirs remain (its hook makes a git commit, hence the `git config` steps in CI); `test_issues.py` unit-tests the issue body/marker helpers. Neither needs network or a token.

### Testing the template end-to-end (what CI does)
```bash
# Render the template from the current working tree
cruft create . --no-input --extra-context='{"package_name":"package_alt"}'
cd project-name
git add .
pre-commit run --all-files      # lint the generated project
uv run python -c "import package_alt"
hatch run docs:build            # build generated docs (needs pandoc installed)
```
CI matrixes over Python 3.11 & 3.14 and over a `package_name` that matches the default derivation vs. one that doesn't (`package_alt`) — always consider both cases when touching name-dependent template logic.

### Linting
```bash
pre-commit run --all-files
```
`.pre-commit-config.yaml` here covers the template repo itself: `biome-format` (JSON/JS via `biome.jsonc`), `ruff` + `pyproject-fmt` scoped to `scripts/`, and `codespell`. The generated project ships its own separate pre-commit config.

## Conventions

- Ruff in `scripts/` enforces `from __future__ import annotations` (required-import) and a broad lint set; types used only for annotations go under `if TYPE_CHECKING:`.
- When editing template files, remember output is the *rendered* result — test a representative `cruft create` rather than eyeballing Jinja.
- Releasing a new template version = creating a GitHub release with a `vX.X.X` tag; this automatically fans out cruft PRs to downstream packages, so treat releases as user-facing changes.
