#!/bin/env python
from subprocess import run

run("git init --initial-branch=main .".split(), check=True)
