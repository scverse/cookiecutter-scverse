from __future__ import annotations

from logging import basicConfig, getLogger

from rich.logging import RichHandler

log = getLogger(__name__)


def setup_logging() -> None:
    basicConfig(level="INFO", handlers=[RichHandler()])
