"""Module defining functions for handling serialization of wide variety of Python data types."""

from base64 import urlsafe_b64encode
from collections import ChainMap, Counter, OrderedDict, UserList, UserString, defaultdict, deque
from collections.abc import Set
from dataclasses import asdict
from datetime import date, datetime, time, timedelta, timezone
from decimal import Context, Decimal, DecimalTuple
from enum import Enum, EnumMeta, EnumType, Flag, IntEnum, IntFlag
from functools import lru_cache
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from os import PathLike
from pathlib import Path, PosixPath, PurePath, WindowsPath
from re import Match, Pattern
from traceback import format_exception, format_tb
from types import TracebackType
from typing import Any, TypeGuard
from uuid import UUID

from arclog.types.aliases import TypeHandlersMap
from arclog.types.protocols import DataclassProtocol, NamedTupleProtocol

__all__ = ('TYPEMAP',)


# --------------------------- 'Type' Types (Classes) ---------------------------
def use_type_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[type]:
    """Function to check for `type` types (a.k.a. classes)."""
    return isinstance(obj, type)


def type_default(obj: type, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `type` types (a.k.a. classes)."""
    return obj.__name__


# --------------------------- Builtin/Basic Types -----------------------------
def use_builtin_default(
    obj: Any, *args: Any, **kwargs: Any
) -> TypeGuard[int | float | bool | str | list | dict | tuple]:
    """Function to check for builtin/basic types."""
    return isinstance(obj, int | float | bool | str | list | dict | tuple)


def builtin_default(
    obj: int | float | bool | str | list | dict | tuple, *args: Any, **kwargs: Any
) -> Any:
    """Function to handle encoding of builtin/basic types."""
    return obj


# ------------------ NamedTuple/collections.namedtuple Types -------------------
def use_namedtuple_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[NamedTupleProtocol]:
    """Function to check for `NamedTuple`/`collections.namedtuple` types."""
    attr = ('_field_defaults', '_fields', '_asdict')
    return isinstance(obj, tuple) and all(hasattr(obj, _) for _ in attr)


def namedtuple_default(obj: NamedTupleProtocol, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Function to handle encoding of `NamedTuple`/`collections.namedtuple` types."""
    return obj._asdict()


# --------------------------------- Set Types ----------------------------------
def use_set_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[set | frozenset | Set]:
    """Function to check for `set` types."""
    return isinstance(obj, set | frozenset | Set)


def set_default(obj: set, *args: Any, **kwargs: Any) -> list:
    """Function to handle encoding of `set` types."""
    return list(obj)


# -------------------------------- Bytes Types ---------------------------------
def use_bytes_default(
    obj: Any, *args: Any, **kwargs: Any
) -> TypeGuard[bytes | bytearray | memoryview]:
    """Function to check for `bytes`, `bytearray`, and `memoryview` types."""
    return isinstance(obj, bytes | bytearray | memoryview)


def bytes_default(obj: bytes, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding/decoding of `bytes`, `bytearray`, and `memoryview` types."""
    return urlsafe_b64encode(obj).decode('utf-8')


# ---------------------------- datetime.time Types -----------------------------
def use_datetime_time_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[time]:
    """Function to check for `datetime.time` types."""
    return isinstance(obj, time)


def datetime_time_default(obj: time, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `datetime.time` types."""
    return obj.isoformat()


# ---------------------------- datetime.date Types -----------------------------
def use_datetime_date_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[date]:
    """Function to check for `datetime.date` types."""
    return isinstance(obj, date)


def datetime_date_default(obj: date, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `datetime.date` types."""
    return obj.isoformat()


# -------------------------- datetime.datetime Types ---------------------------
def use_datetime_datetime_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[datetime]:
    """Function to check for `datetime.datetime` types."""
    return isinstance(obj, datetime)


def datetime_datetime_default(obj: datetime, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `datetime.datetime` types."""
    return obj.isoformat()


# -------------------------- datetime.timedelta Types --------------------------
def use_datetime_timedelta_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[timedelta]:
    """Function to check for `datetime.timedelta` types."""
    return isinstance(obj, timedelta)


def datetime_timedelta_default(obj: timedelta, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `datetime.timedelta` types."""
    return str(obj.total_seconds())


# -------------------------- datetime.timezone Types ---------------------------
def use_datetime_timezone_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[timezone]:
    """Function to check for `datetime.timezone` types."""
    return isinstance(obj, timezone)


def datetime_timezone_default(obj: timezone, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `datetime.timezone` types."""
    return obj.tzname(None)


# --------------------------------- Enum Types ---------------------------------
def use_enum_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[Enum]:
    """Function to check for `enum` types."""
    return (
        isinstance(obj, Enum | EnumType)
        or (isinstance(obj, type) and issubclass(obj, Enum))
        or obj is EnumType
        or obj is EnumMeta
    )


def enum_default(obj: Enum, *args: Any, **kwargs: Any) -> Any | list[Any]:
    """Function to handle encoding of `enum` types."""
    return obj.value


# ------------------------------- EnumMeta Types -------------------------------
def use_enum_meta_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[EnumMeta]:
    """Function to check for `enum.EnumMeta` types."""
    return obj is EnumMeta


def enum_meta_default(obj: EnumMeta, *args: Any, **kwargs: Any) -> list[Any]:
    """Function to handle encoding of `enum.EnumMeta` types."""
    return [e.value for e in obj]


# ------------------------------- EnumType Types -------------------------------
def use_enum_type_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[EnumType]:
    """Function to check for `enum.EnumType` types."""
    return obj is EnumType


def enum_type_default(obj: EnumType, *args: Any, **kwargs: Any) -> list[Any]:
    """Function to handle encoding of `enum.EnumType` types."""
    return [e.value for e in obj]


# ------------------------------- IntEnum Types --------------------------------
def use_int_enum_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[IntEnum]:
    """Function to check for `enum.IntEnum` types."""
    return isinstance(obj, IntEnum)


def int_enum_default(obj: IntEnum, *args: Any, **kwargs: Any) -> int:
    """Function to handle encoding of `enum.IntEnum` types."""
    return obj.value


# --------------------------------- Flag Types ---------------------------------
def use_flag_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[Flag]:
    """Function to check for `enum.Flag` types."""
    return isinstance(obj, Flag)


def flag_default(obj: Flag, *args: Any, **kwargs: Any) -> int:
    """Function to handle encoding of `enum.Flag` types."""
    return obj.value


# ------------------------------- IntFlag Types --------------------------------
def use_int_flag_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[IntFlag]:
    """Function to check for `enum.IntFlag` types."""
    return isinstance(obj, IntFlag)


def int_flag_default(obj: IntFlag, *args: Any, **kwargs: Any) -> int:
    """Function to handle encoding of `enum.IntFlag` types."""
    return obj.value


# ---------------------------- Complex Number Types ----------------------------
def use_complex_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[complex]:
    """Function to check for `complex` types."""
    return isinstance(obj, complex)


def complex_default(obj: complex, *args: Any, **kwargs: Any) -> tuple[float, float]:
    """Function to handle encoding of `complex` types."""
    return (obj.real, obj.imag)


# -------------------------------- Deque Types ---------------------------------
def use_deque_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[deque]:
    """Function to check for `collections.deque` types."""
    return isinstance(obj, deque)


def deque_default(obj: deque, *args: Any, **kwargs: Any) -> list:
    """Function to handle encoding of `collections.deque` types."""
    return list(obj)


# ------------------------------ Exception Types -------------------------------
def use_exception_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[BaseException]:
    """Function to check for `BaseException` types."""
    return isinstance(obj, BaseException)


def exception_default(obj: BaseException, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `BaseException` types."""
    if hasattr(obj, '__traceback__'):
        return ''.join(format_exception(type(obj), obj, obj.__traceback__)).strip()
    return f'{obj.__class__.__name__}: {obj}'


# ------------------------------ Traceback Types -------------------------------
def use_traceback_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[TracebackType]:
    """Function to check for `TracebackType` types."""
    return isinstance(obj, TracebackType)


def traceback_default(obj: TracebackType, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `TracebackType` types."""
    return ''.join(format_tb(obj)).strip()


# ------------------------------ UserString Types ------------------------------
def use_userstring_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[UserString]:
    """Function to check for `collections.UserString` types."""
    return isinstance(obj, UserString)


def userstring_default(obj: UserString, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `collections.UserString` types."""
    return str(obj)


# ------------------------------- UserList Types -------------------------------
def use_userlist_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[UserList]:
    """Function to check for `collections.UserList` types."""
    return isinstance(obj, UserList)


def userlist_default(obj: UserList, *args: Any, **kwargs: Any) -> list:
    """Function to handle encoding of `collections.UserList` types."""
    return list(obj)


# ------------------------------- ChainMap Types -------------------------------
def use_chainmap_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[ChainMap]:
    """Function to check for `collections.ChainMap` types."""
    return isinstance(obj, ChainMap)


def chainmap_default(obj: ChainMap, *args: Any, **kwargs: Any) -> list[dict]:
    """Function to handle encoding of `collections.ChainMap` types."""
    return [dict(m) for m in obj.maps]


# ------------------------------- Counter Types --------------------------------
def use_counter_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[Counter]:
    """Function to check for `collections.Counter` types."""
    return isinstance(obj, Counter)


def counter_default(obj: Counter, *args: Any, **kwargs: Any) -> dict:
    """Function to handle encoding of `collections.Counter` types."""
    return dict(obj)


# ----------------------------- defaultdict Types ------------------------------
def use_defaultdict_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[defaultdict]:
    """Function to check for `collections.defaultdict` types."""
    return isinstance(obj, defaultdict)


def defaultdict_default(obj: defaultdict, *args: Any, **kwargs: Any) -> dict:
    """Function to handle encoding of `collections.defaultdict` types."""
    return dict(obj)


# ----------------------------- OrderedDict Types ------------------------------
def use_ordereddict_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[OrderedDict]:
    """Function to check for `collections.OrderedDict` types."""
    return isinstance(obj, OrderedDict)


def ordereddict_default(obj: OrderedDict, *args: Any, **kwargs: Any) -> dict:
    """Function to handle encoding of `collections.OrderedDict` types."""
    return dict(obj)


# ------------------------------ Dataclass Types -------------------------------
def use_dataclass_default(obj: Any, *args: Any, **kwargs: Any) -> bool:
    """Function to check for `dataclasses.dataclass` types."""
    return hasattr(obj, '__dataclass_fields__') and not isinstance(obj, type)


def dataclass_default(obj: DataclassProtocol, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Function to handle encoding of `dataclasses.dataclass` types."""
    return asdict(obj)


# ------------------------------- Decimal Types --------------------------------
def use_decimal_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[Decimal]:
    """Function to check for `decimal.Decimal` types."""
    return isinstance(obj, Decimal)


def decimal_default(obj: Decimal, *args: Any, **kwargs: Any) -> int | float:
    """Function to handle encoding of `decimal.Decimal` types."""
    exponent = obj.as_tuple().exponent
    if isinstance(exponent, int) and exponent >= 0:
        return int(obj)
    return float(obj)


# ------------------------------- Context Types --------------------------------
def use_context_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[Context]:
    """Function to check for `decimal.Context` types."""
    return isinstance(obj, Context)


def context_default(obj: Context, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Function to handle encoding of `decimal.Context` types."""
    return {
        'prec': obj.prec,
        'rounding': obj.rounding,
        'Emin': obj.Emin,
        'Emax': obj.Emax,
        'capitals': obj.capitals,
        'clamp': obj.clamp,
        'flags': list(obj.flags),
        'traps': list(obj.traps),
    }


# ---------------------------- DecimalTuple Types ------------------------------
def use_decimal_tuple_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[DecimalTuple]:
    """Function to check for `decimal.DecimalTuple` types."""
    return isinstance(obj, DecimalTuple)


def decimal_tuple_default(obj: DecimalTuple, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Function to handle encoding of `decimal.DecimalTuple` types."""
    return {
        'sign': obj.sign,
        'digits': list(obj.digits),
        'exponent': obj.exponent,
    }


# ----------------------------- IPv6Address Types ------------------------------
def use_ipv6address_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[IPv6Address]:
    """Function to check for `IPv6Address` types."""
    return isinstance(obj, IPv6Address)


def ipv6address_default(obj: IPv6Address, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `IPv6Address` types."""
    return str(obj)


# ---------------------------- IPv6Interface Types -----------------------------
def use_ipv6interface_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[IPv6Interface]:
    """Function to check for `IPv6Interface` types."""
    return isinstance(obj, IPv6Interface)


def ipv6interface_default(obj: IPv6Interface, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `IPv6Interface` types."""
    return str(obj)


# ----------------------------- IPv6Network Types ------------------------------
def use_ipv6network_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[IPv6Network]:
    """Function to check for `IPv6Network` types."""
    return isinstance(obj, IPv6Network)


def ipv6network_default(obj: IPv6Network, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `IPv6Network` types."""
    return str(obj)


# ----------------------------- IPv4Address Types ------------------------------
def use_ipv4address_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[IPv4Address]:
    """Function to check for `IPv4Address` types."""
    return isinstance(obj, IPv4Address)


def ipv4address_default(obj: IPv4Address, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `IPv4Address` types."""
    return str(obj)


# ---------------------------- IPv4Interface Types -----------------------------
def use_ipv4interface_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[IPv4Interface]:
    """Function to check for `IPv4Interface` types."""
    return isinstance(obj, IPv4Interface)


def ipv4interface_default(obj: IPv4Interface, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `IPv4Interface` types."""
    return str(obj)


# ----------------------------- IPv4Network Types ------------------------------
def use_ipv4network_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[IPv4Network]:
    """Function to check for `IPv4Network` types."""
    return isinstance(obj, IPv4Network)


def ipv4network_default(obj: IPv4Network, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `IPv4Network` types."""
    return str(obj)


# ------------------------------ PurePath Types --------------------------------
def use_purepath_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[PurePath]:
    """Function to check for `pathlib.PurePath` types."""
    return isinstance(obj, PurePath)


def purepath_default(obj: PurePath, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `pathlib.PurePath` types."""
    return str(obj)


# ------------------------------- Path Types -----------------------------------
def use_path_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[Path]:
    """Function to check for `pathlib.Path` types."""
    return isinstance(obj, Path)


def path_default(obj: Path, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `pathlib.Path` types."""
    return str(obj)


# ----------------------------- PosixPath Types --------------------------------
def use_posixpath_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[PosixPath]:
    """Function to check for `pathlib.PosixPath` types."""
    return isinstance(obj, PosixPath)


def posixpath_default(obj: PosixPath, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `pathlib.PosixPath` types."""
    return str(obj)


# ---------------------------- WindowsPath Types -------------------------------
def use_windowspath_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[WindowsPath]:
    """Function to check for `pathlib.WindowsPath` types."""
    return isinstance(obj, WindowsPath)


def windowspath_default(obj: WindowsPath, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `pathlib.WindowsPath` types."""
    return str(obj)


# ----------------------------- PathLike Types ---------------------------------
def use_pathlike_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[PathLike]:
    """Function to check for `os.PathLike` types."""
    return isinstance(obj, PathLike)


def pathlike_default(obj: PathLike, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `os.PathLike` types."""
    return str(obj)


# ------------------------------- Pattern Types --------------------------------
def use_pattern_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[Pattern]:
    """Function to check for `re.Pattern` types."""
    return isinstance(obj, Pattern)


def pattern_default(obj: Pattern, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `re.Pattern` types."""
    return obj.pattern


# ------------------------------- Match Types ----------------------------------
def use_match_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[Match]:
    """Function to check for `re.Match` types."""
    return isinstance(obj, Match)


def match_default(obj: Match, *args: Any, **kwargs: Any) -> dict[str, Any]:
    """Function to handle encoding of `re.Match` types."""
    return {
        'string': obj.string,
        're': obj.re.pattern,
        'groups': obj.groups(),
        'groupdict': obj.groupdict(),
        'start': obj.start(),
        'end': obj.end(),
        'span': obj.span(),
    }


# --------------------------------- UUID Types ---------------------------------
def use_uuid_default(obj: Any, *args: Any, **kwargs: Any) -> TypeGuard[UUID]:
    """Function to check for `uuid.UUID` types."""
    return isinstance(obj, UUID)


def uuid_default(obj: UUID, *args: Any, **kwargs: Any) -> str:
    """Function to handle encoding of `uuid.UUID` types."""
    return str(obj)


# ----------------------------- Type Handlers Map ------------------------------
@lru_cache(maxsize=1)
def _get_typemap() -> TypeHandlersMap:
    mapping: TypeHandlersMap = {}
    for name, func in globals().items():
        if name.startswith('use_'):
            encoder_name = name.replace('use_', '')
            encoder_func = globals().get(encoder_name)
            if encoder_func and callable(encoder_func):
                mapping[func] = encoder_func
    return mapping


TYPEMAP = _get_typemap()
