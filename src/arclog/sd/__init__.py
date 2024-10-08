"""Single dispatch serializer subpackage."""

from collections import defaultdict
from collections.abc import Callable
from functools import singledispatch
from typing import Any, get_type_hints

from arclog.exceptions import MissingAnnotationError
from arclog.sd.serializers import TYPEMAP
from arclog.types import TypeHandlersMap

_validation_cache: defaultdict[Callable[..., Any], bool] = defaultdict(bool)
_excepted_handlers: TypeHandlersMap = {}


def unknown_default(obj: Any, *args: Any, **kwargs: Any) -> str:
    try:
        return str(obj)
    except Exception:  # noqa: S110
        pass
    try:
        return repr(obj)
    except Exception:  # noqa: S110
        pass
    return '__failed_to_encode__'


@singledispatch
def serialize(obj: Any, *args: Any, _raise: bool = True, **kwargs: Any) -> Any:
    for k, v in TYPEMAP.items():
        if k(obj):
            return v(obj)
    if _raise:
        raise NotImplementedError
    return unknown_default(obj)


def _validate_type_handler(fn: Callable[..., Any]) -> None:
    annotations = get_type_hints(fn)
    if 'obj' not in annotations:
        raise MissingAnnotationError(fn)
    _validation_cache[fn] = True


def _validate_typemap(typemap: TypeHandlersMap) -> None:
    for k, v in typemap.items():
        if _validation_cache[v] is not True:
            _validate_type_handler(v)
        if _validation_cache[k] is not True:
            _validate_type_handler(k)


def _register_singledispatch() -> None:
    global _excepted_handlers
    _validate_typemap(TYPEMAP)
    for k, v in TYPEMAP.items():
        try:
            typ = v.__annotations__['obj']
            serialize.register(typ, v)
        except TypeError:
            _excepted_handlers[k] = v


_register_singledispatch()
