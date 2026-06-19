#!/usr/bin/env python3
"""Deterministic groundwork for an agent-driven cookiecutter-scverse template update.

This does the *mechanical* part of a template sync and stops short of any decision
that benefits from judgement. It renders the template twice using the downstream
repo's own cookiecutter answers:

  * ``render_old`` — the template at the commit the repo was last synced to
    (the ``commit`` field in ``.cruft.json``)
  * ``render_new`` — the template at the requested new tag

Comparing ``render_old`` vs ``render_new`` tells us exactly what the *template*
changed between the two versions (the modernization we want to propagate).
Comparing each render against the repo's current file tells us whether the repo
ever diverged. Cross-tabulating the three produces a per-file classification that
the agent then acts on (see SKILL.md).

It writes nothing into the target repo. Output: the two render trees plus a
``manifest.json`` (and a human-readable summary on stdout).

Usage:
    python sync_helper.py --repo PATH --tag TAG [--template PATH_OR_URL] \
        [--workdir DIR] [--old-ref REF]

Requires ``cruft`` to be importable/runnable (``python -m cruft``); install it on the
fly with e.g. ``uvx --from cruft python sync_helper.py ...`` if it isn't present.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# cruft create fails if these template-config vars differ from the template default,
# so we must not feed them back in as extra context (see cruft#166).
IGNORE_COOKIECUTTER_VARS = ["_copy_without_render"]

# How much of each old->new template diff to embed in the manifest before truncating.
MAX_DIFF_CHARS = 8000


def sh(cmd: list[str], **kw) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, text=True, capture_output=True, **kw)


def read_cruft_json(repo: Path) -> dict:
    cruft_file = repo / ".cruft.json"
    if not cruft_file.is_file():
        sys.exit(f"error: {cruft_file} not found — repo is not linked to the template, nothing to sync.")
    return json.loads(cruft_file.read_text())


def clone_or_link_template(template: str, workdir: Path) -> Path:
    """Return a local path to the template git repo (clone it if a URL was given)."""
    if Path(template).expanduser().is_dir():
        return Path(template).expanduser().resolve()
    dest = workdir / "template"
    print(f"Cloning template {template} -> {dest}")
    sh(["git", "clone", "--filter=blob:none", template, str(dest)])
    return dest


def resolve_commit(template_dir: Path, ref: str) -> str:
    return sh(["git", "-C", str(template_dir), "rev-list", "-n1", ref]).stdout.strip()


def render(template_dir: Path, ref: str, context: dict, out: Path, project_name: str) -> Path:
    """Render the template at `ref` with `context` into `out`; return the project dir."""
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({k: v for k, v in context.items() if k not in IGNORE_COOKIECUTTER_VARS}, f)
        ctx_file = f.name
    cmd = [
        sys.executable, "-m", "cruft", "create", str(template_dir),
        f"--checkout={ref}", "--no-input", f"--extra-context-file={ctx_file}",
        "--output-dir", str(out),
    ]
    print("Running:", " ".join(cmd))
    # cruft runs the template's post-gen hook (git commit, pre-commit install); that is
    # expected to succeed exactly as it does in the production sync. Surface output on failure.
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        sys.exit(f"cruft create at {ref} failed:\n{proc.stdout}\n{proc.stderr}")
    project = out / project_name
    if not project.is_dir():
        # fall back to the single generated directory if project_name was overridden
        subdirs = [p for p in out.iterdir() if p.is_dir()]
        if len(subdirs) != 1:
            sys.exit(f"could not locate rendered project under {out}: {subdirs}")
        project = subdirs[0]
    return project


def list_files(root: Path) -> set[str]:
    return {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and ".git/" not in f"{p.relative_to(root)}/"
    }


def same(a: Path, b: Path) -> bool:
    try:
        return a.read_bytes() == b.read_bytes()
    except OSError:
        return False


def unified_diff(old: Path, new: Path, rel: str) -> str:
    """Best-effort old->new template diff for a single file (the template's *intent*)."""
    try:
        proc = subprocess.run(
            ["git", "diff", "--no-index", "--no-color", str(old), str(new)],
            text=True, capture_output=True,
        )
        out = proc.stdout
    except OSError:
        out = ""
    if len(out) > MAX_DIFF_CHARS:
        out = out[:MAX_DIFF_CHARS] + "\n... [diff truncated] ...\n"
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", required=True, type=Path, help="path to the downstream repo checkout")
    ap.add_argument("--tag", required=True, help="new template release tag to update to")
    ap.add_argument("--template", help="template path or URL (default: 'template' field in .cruft.json)")
    ap.add_argument("--old-ref", help="override the old template ref (default: 'commit' field in .cruft.json)")
    ap.add_argument("--workdir", type=Path, help="scratch dir for renders (default: a temp dir)")
    args = ap.parse_args()

    repo = args.repo.expanduser().resolve()
    workdir = (args.workdir or Path(tempfile.mkdtemp(prefix="tmpl-sync-"))).resolve()
    workdir.mkdir(parents=True, exist_ok=True)

    cruft = read_cruft_json(repo)
    context = cruft["context"]["cookiecutter"]
    project_name = context["project_name"]
    template_src = args.template or cruft["template"]
    old_ref = args.old_ref or cruft["commit"]

    template_dir = clone_or_link_template(template_src, workdir)
    old_commit = resolve_commit(template_dir, old_ref)
    new_commit = resolve_commit(template_dir, args.tag)

    render_old = render(template_dir, old_commit, context, workdir / "render_old", project_name)
    render_new = render(template_dir, args.tag, context, workdir / "render_new", project_name)

    old_files = list_files(render_old)
    new_files = list_files(render_new)
    repo_files = list_files(repo)

    cats: dict[str, list] = {
        "template_added": [],                 # new file the template introduces
        "template_removed": [],               # file the template dropped
        "template_modified_repo_clean": [],   # template changed it AND repo still matches old -> safe to take new
        "template_modified_repo_diverged": [],# template changed it AND repo diverged -> needs judgement (3-way)
        "template_unchanged": [],             # template identical old==new -> informational, leave repo alone
    }

    for rel in sorted(old_files | new_files):
        in_old, in_new = rel in old_files, rel in new_files
        o, n, r = render_old / rel, render_new / rel, repo / rel
        if in_new and not in_old:
            entry = {"path": rel, "in_repo": rel in repo_files}
            if rel in repo_files and not same(n, r):
                entry["note"] = "repo already has a differing version"
            cats["template_added"].append(entry)
        elif in_old and not in_new:
            cats["template_removed"].append({"path": rel, "in_repo": rel in repo_files})
        elif same(o, n):
            cats["template_unchanged"].append(rel)
        elif rel not in repo_files:
            # template changed it but the repo deleted it — treat as a divergence to judge
            cats["template_modified_repo_diverged"].append(
                {"path": rel, "repo_state": "deleted", "template_diff": unified_diff(o, n, rel)}
            )
        elif same(o, r):
            cats["template_modified_repo_clean"].append(rel)
        else:
            cats["template_modified_repo_diverged"].append(
                {"path": rel, "repo_state": "modified", "template_diff": unified_diff(o, n, rel)}
            )

    repo_only = sorted(repo_files - old_files - new_files)

    manifest = {
        "project_name": project_name,
        "repo": str(repo),
        "template": str(template_dir),
        "old_ref": old_ref,
        "old_commit": old_commit,
        "new_tag": args.tag,
        "new_commit": new_commit,
        "render_old": str(render_old),
        "render_new": str(render_new),
        "cruft_skip": cruft.get("context", {}).get("cookiecutter", {}).get("_exclude_on_template_update", []),
        "tool_cruft_skip_hint": "also read [tool.cruft] skip in the repo's pyproject.toml",
        "categories": cats,
        "repo_only_files": repo_only,
    }
    (workdir / "manifest.json").write_text(json.dumps(manifest, indent=2))

    # human-readable summary
    print("\n" + "=" * 72)
    print(f"Template update plan: {project_name}  {old_commit[:8]} -> {args.tag} ({new_commit[:8]})")
    print("=" * 72)
    print(f"render_old : {render_old}")
    print(f"render_new : {render_new}")
    print(f"manifest   : {workdir / 'manifest.json'}\n")
    print(f"  template_added                  : {len(cats['template_added'])}")
    print(f"  template_removed                : {len(cats['template_removed'])}")
    print(f"  template_modified_repo_clean    : {len(cats['template_modified_repo_clean'])}  (safe to take new)")
    print(f"  template_modified_repo_diverged : {len(cats['template_modified_repo_diverged'])}  (NEEDS JUDGEMENT)")
    print(f"  template_unchanged              : {len(cats['template_unchanged'])}  (leave repo as-is)")
    print(f"  repo_only_files                 : {len(repo_only)}  (project content, do not touch)")
    print("\nNext: follow SKILL.md to reconcile the 'diverged' files and apply the rest.")


if __name__ == "__main__":
    main()
