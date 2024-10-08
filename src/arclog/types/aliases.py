"""TypeAlias types module."""

from collections.abc import Callable, MutableMapping
from typing import Any, TypeGuard

type AnyCallable = Callable[..., Any]
type AnyCallableTypeGuard = Callable[..., TypeGuard[Any] | bool]
type TypeHandlersMap = MutableMapping[AnyCallableTypeGuard, AnyCallable]
