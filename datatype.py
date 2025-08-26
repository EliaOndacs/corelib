from typing import Any, Callable, Literal
from functools import wraps
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
EXIT_SUCCESSFUL = 0


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
