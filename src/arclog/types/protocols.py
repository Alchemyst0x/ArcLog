"""Protocol types module."""

from typing import Any, ClassVar, Protocol, runtime_checkable

__all__ = (
    'DataclassProtocol',
    'NamedTupleProtocol',
    'Logger',
)


@runtime_checkable
class DataclassProtocol(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Any]]


@runtime_checkable
class NamedTupleProtocol(Protocol):
    _field_defaults: ClassVar[dict[str, Any]]
    _fields: ClassVar[tuple[str, ...]]

    def _asdict() -> dict: ...


class Logger(Protocol):
    """Logger protocol."""

    def debug(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Log an event at log level `DEBUG`."""

    def info(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Log an event at log level `INFO`."""

    def warning(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Log an event at log level `WARNING`."""

    def warn(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Log an event at log level `WARN`."""

    def error(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Log an event at log level `ERROR`."""

    def fatal(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Log an event at log level `FATAL`."""

    def exception(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Log an event at log level `ERROR`."""

    def critical(self, event: str, *args: Any, **kwargs: Any) -> Any:
        """Log an event at log level `CRITICAL`."""

    def setLevel(self, level: int) -> None:  # noqa: N802
        """Set the log level for this logger."""
