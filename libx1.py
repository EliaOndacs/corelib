from typing import Literal
import re

class Bool:
    def __init__(self, value: Literal[0, 1, 2]) -> None:
        self.__alloc__ = value

    def __repr__(self) -> str:
        match self.__alloc__:
            case 0:
                return "False"
            case 1:
                return "True"
            case 2:
                return "Maybe"
        return "undefined"

    def tobool(self) -> bool | str:
        match self.__alloc__:
            case 0:
                return False
            case 1:
                return True
            case 2:
                raise TypeError(
                    "invalid convertion from type `Bool<Maybe>` to python builtin."
                )
        return "undefined"


def equal(a, b):
    return a == b


def isFalse(a):
    return a == False


def make(type_obj, *args, **kwargs):
    return type_obj(*args, **kwargs)


def findPattern(pattern, string):
    return re.search(pattern, string)
