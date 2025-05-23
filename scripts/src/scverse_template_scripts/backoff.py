from __future__ import annotations

import random
import time
from typing import TYPE_CHECKING

from ._log import log

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import TypeVar

    T = TypeVar("T")


def retry_with_backoff(
    fn: Callable[[], T],
    retries: int = 5,
    backoff_in_seconds: int | float = 1,
    exc_cls: type = Exception,
) -> T:
    exc = None
    for x in range(retries):
        try:
            return fn()
        except exc_cls as _exc:
            exc = _exc
            sleep = backoff_in_seconds * 2**x + random.uniform(0, 1)
            log.info(f"Action failed. Retrying in {sleep}s.")
            time.sleep(sleep)
    raise exc
