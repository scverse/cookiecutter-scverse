#!/bin/env python3
from subprocess import run

# Check if git user.name and user.email are configured --> fail early if it's not set
run(["git", "config", "user.name"], check=True)
run(["git", "config", "user.email"], check=True)

# use 'main' as default branch irrespective of git configuration
run(["git", "init", "--initial-branch=main", "."], check=True)
