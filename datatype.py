from typing import Any, TypedDict, Literal, Callable, Optional, Type

type Treenode[T] = tuple[T, list[Treenode[T]]]
type Treeroot[T] = list[Treenode[T]]

type static[T] = T
type dynamic[T] = T
type mutable[T] = T
type unmutable[T] = T

type string = str
type integer = int
type boolean = bool
type array = list

type pointer[T] = int
type carry[T] = T
NULL = 0
EXIT_FAILURE = -1
EXIT_SUCCESSFULL = 0

class bind[T]:
    def __init__(self, obj: T) -> None:
        self.obj_id: int = id(obj)
        self.obj_name: str = type(obj).__name__
        self.obj: T = obj

    def __get__(self, *_):
        return self.obj

    def __repr__(self) -> str:
        return repr(self.obj)


class Error:
    def __init__(self, name: str, message: str) -> None:
        self.name = name
        self.message = message

    def __repr__(self) -> str:
        return f"{self.name}:\n{self.message}"

    @classmethod
    def new(cls, name: str, message: str) -> "Error":
        return Error(name, message)


class Object:
    @classmethod
    def new[T](cls, obj: type[T], *args, **kwargs) -> T:
        new = obj.__new__(obj)
        if hasattr(new, "__init__"):
            new.__init__(*args, **kwargs) # type: ignore
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

def getpage(Book: book, page: int) -> str|None:
    "gets the content of a page from a book"
    return Book.get(page, None)

def delpage(Book: book, page: int) -> Literal[-1]|book:
    "reset a page content in a book"
    if not (page in Book):
        return -1
    return setpage(Book, page, "")

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
