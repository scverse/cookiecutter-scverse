#!/bin/sh

# Update pre commit hooks
pre-commit autoupdate -c .pre-commit-config.yaml
pre-commit install

# Upload to github
# gh repo create --push
