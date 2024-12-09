from dataclasses import dataclass
from typing import Any, Callable

type __Namespace_value__ = int | str | Callable | "Namespace" | list
type Namespace = dict[str, __Namespace_value__]


def setvar(self: Namespace, key: str, value: __Namespace_value__):
    self[key] = value
    return


def getvar(self: Namespace, key: str) -> __Namespace_value__:
    return self[key]
