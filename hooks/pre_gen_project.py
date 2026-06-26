#!/bin/env python3
import sys
from subprocess import run


def git_config_get(key: str) -> str | None:
    """Return the value of a git config key, or an empty string if it is not set."""
    result = run(["git", "config", key], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


# use 'main' as default branch irrespective of git configuration
run(["git", "init", "--initial-branch=main", "."], check=True)

# Resolve the author identity for the initial commit.
# We do *not* mandate a global git config: some users configure git per-repository only.
# Prefer an existing git config (global or system) and fall back to the values the user
# entered in cookiecutter.
name = git_config_get("user.name") or "{{ cookiecutter.author_full_name }}".strip()
email = git_config_get("user.email") or "{{ cookiecutter.author_email }}".strip()

if not name or not email:
    sys.exit(
        "ERROR: could not determine an author name/email for the initial commit.\n"
        "Either configure git (`git config --global user.name ...` and "
        "`git config --global user.email ...`) or provide the author name/email "
        "when prompted by the template."
    )

# Set the identity at the repo level only when it is not already resolvable from existing
# git config, so we never clobber the user's real git identity.
if not git_config_get("user.name"):
    run(["git", "config", "user.name", name], check=True)
if not git_config_get("user.email"):
    run(["git", "config", "user.email", email], check=True)
