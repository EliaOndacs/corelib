"""
a library for data generation

"""

import re
from types import FunctionType, ModuleType
from typing import Any, Callable, Protocol


class SupportsStr(Protocol):
    def __str__(self) -> str: ...


def datamodel(model: dict[str, type]):
    """
    allows you to make datamodel's that you can use later
    to make structured data
    """

    def __call__(**kwargs) -> dict:
        new: dict[str, Any] = {}
        for key in model:
            value = kwargs.get(key, None)
            if not value:
                raise KeyError(f"key {key!r} not found in the provided data")
            if type(value).__name__ != model[key].__name__:
                raise TypeError(
                    f"key {key!r} should be a type of {model[key].__name__!r}, found {type(value).__name__!r} instead"
                )
            new[key] = value
        return new

    return __call__


def repeat(data: SupportsStr, times: int):
    return str(data) * times


def string(data: SupportsStr):
    return str(data)


def number(data: str | int):
    try:
        return int(data)
    except:
        raise ValueError(f"expected a integer number, got {data!r} instead!")


def boolean(data: str):
    match data:
        case "true" | "True":
            return True
        case "false" | "False":
            return False
    raise ValueError(
        f"expected a string of 'true|True' or 'false|False', got {data!r} instead!"
    )


def array(data: str):
    return data.split(",")


def apply[T](data: list[T], transform: Callable[[T], Any]) -> list[Any | T]:
    return list(filter(transform, data))


def retype(value: str):
    number_pattern = r"^-?\d+$"
    boolean_pattern = r"^(true|True|false|False)$"
    ismatch = lambda b: bool(re.match(value, b))
    if ismatch(number_pattern):
        return number(value)
    elif ismatch(boolean_pattern):
        return boolean(value)
    return string(value)


def groupBy[T](data: list[T], key_func: Callable[[T], Any]):
    grouped: dict = {}
    for item in data:
        key = key_func(item)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(item)
    return grouped


def pymodule(name: str, namespace: dict) -> ModuleType:
    module = ModuleType(name)
    exec(f"globals().update({namespace})", module.__dict__)
    return module

