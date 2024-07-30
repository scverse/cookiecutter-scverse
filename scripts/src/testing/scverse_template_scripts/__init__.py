"""Temporary directory and git fixtures"""

from __future__ import annotations

from typing import TYPE_CHECKING

from git import Repo

if TYPE_CHECKING:
    from pathlib import Path


class GitRepo:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace
        self.api = Repo.init(self.workspace)
        self.uri = f"file://{self.workspace}"
