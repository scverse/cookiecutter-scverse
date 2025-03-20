from __future__ import annotations

from logging import basicConfig, getLogger

log = getLogger(__name__)


def setup_logging() -> None:
    from rich.logging import RichHandler

    basicConfig(level="INFO", handlers=[RichHandler()])
