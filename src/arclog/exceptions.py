from collections.abc import Callable
from typing import Any


class ArcLogError(Exception):
    """Base `Exception` class from which all ArcLog application errors inherit."""

    def __init__(self, msg: str | list[str] = '', *args: Any) -> None:
        if not isinstance(msg, list):
            msg = [msg]
        msg = ' '.join(str(_) for _ in msg + list(args) if _)
        super().__init__(msg)


class MissingAnnotationError(ArcLogError, TypeError):
    def __init__(self, func: Callable, *args: Any) -> None:
        msg = f"The function '{func.__name__}' must have an 'obj' parameter."
        super().__init__(msg, *args)
