from typing import Any, Callable, Iterable, TypedDict, Literal
from functools import wraps
from warnings import deprecated
from ansi.colour import fg
import sys

type Treenode[T] = tuple[T, list[Treenode[T]]]
type Treeroot[T] = list[Treenode[T]]

type ReadMethod[T] = Callable[[], T]
type WriteMethod[T] = Callable[[T], None]
type AttributeWriter[T] = Callable[[T], T]

type static[T] = T
type dynamic[T] = T
type mutable[T] = T
type unmutable[T] = T

type string = str
type integer = int
type boolean = bool
type array = list

type maybe[T] = T | None

type pointer[T] = int
type carry[T] = T
NULL = 0
EXIT_FAILURE = -1
EXIT_SUCCESSFULL = 0


class Error:
    def __init__(self, name: str, message: str) -> None:
        self.name = name
        self.message = message

    def __repr__(self) -> str:
        return f"{self.name}:\n{self.message}"

    def throw(self):
        "raise the error"
        print(fg.red(repr(self)))
        sys.exit()

    @classmethod
    def new(cls, name: str, message: str) -> "Error":
        return Error(name, message)


type ErrorOrNone = Error | None


class Object:
    @classmethod
    def new[T](cls, obj: type[T], *args, **kwargs) -> T:
        new = obj.__new__(obj)
        if hasattr(new, "__init__"):
            new.__init__(*args, **kwargs)  # type: ignore
        return new

    @classmethod
    def gettype[T](cls, obj: T) -> type[T]:
        return type(obj)

    @classmethod
    def getattr(cls, obj: object, name: str) -> tuple[object, Error | None]:
        if not hasattr(obj, name):
            return None, Error.new(
                "AttributeError", f"attribute {name!r} not found in object {obj!r}"
            )
        return getattr(obj, name), None

    @classmethod
    def setattr(cls, obj: object, name: str, value: object):
        setattr(obj, name, value)

    @classmethod
    def setdict(cls, obj: object, mapping: dict[str, Any]):
        obj.__dict__ = mapping

    @classmethod
    def getdict(cls, obj: object) -> dict[str, Any]:
        return obj.__dict__  # type: ignore


def makeobj(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        namespace = func(*args, **kwargs) or {}
        return type(func.__name__, (object,), namespace)()

    func.__annotations__["return"] = type(func.__name__, (object,), {})
    return wrapper


class char:
    "a type for working with one u8 character"

    @classmethod
    def split(cls, text: str) -> Iterable["char"]:
        r = []
        for c in text:
            r.append(char(c))
        return r

    def __init__(self, char: str):
        if len(char) > 1:
            raise MemoryError(
                f"expected one character but got a string with the length of {len(char)}"
            )
        self._x = char[0].encode()

    def __ne__(self, other: object, /) -> bool:
        return not self.__eq__(other)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, char):
            raise TypeError(
                f"unsupported operation '+' with the type 'char' and {type(other).__name__!r}"
            )
        return self._x == other._x

    def __len__(self):
        return len(self._x)

    def __repr__(self):
        return f"u8{self._x.decode()!r}"

    def __str__(self):
        return self._x.decode()

    def upper(self) -> "char":
        return char(self._x.decode().upper())

    def lower(self) -> "char":
        return char(self._x.decode().lower())

    def join(self, array: Iterable) -> str:
        return self._x.decode().join(array)

    def __add__(self, other: "char") -> bytes:
        if not isinstance(other, char):
            raise TypeError(
                f"unsupported operation '+' with the type 'char' and {type(other).__name__!r}"
            )
        return self._x + other._x

    def __sizeof__(self) -> int:
        return self._x.__sizeof__()


@deprecated("use `corelib/rod.py` type validation library instead!")
class DatatypeBlueprint(TypedDict):
    fields: dict[str, Any]


type book = dict[int, str]
"a type that inherits `dict` for storing data in a `page: text` manner."


def mkbook() -> book:
    "creates a new book object"
    return {}


def setpage(Book: book, page: int, text: str) -> book:
    "set a page content in a book"
    Book[page] = text
    return Book


def getpage(Book: book, page: int) -> str | None:
    "gets the content of a page from a book"
    return Book.get(page, None)


def delpage(Book: book, page: int) -> Literal[-1] | book:
    "reset a page content in a book"
    if not (page in Book):
        return -1
    return setpage(Book, page, "")


@deprecated("use `corelib/rod.py` type validation library instead!")
def check_type(model: dict, blueprint: DatatypeBlueprint) -> bool:
    "returns True if all the types were corrected, False if they were wrong"
    result = True
    if model.keys() != blueprint["fields"].keys():
        result = False
        return result
    for field in model:
        data = model[field]
        if not isinstance(data, blueprint["fields"][field]):
            result = False
    return result
