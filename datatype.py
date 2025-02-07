from typing import Any, TypedDict

type carry[T] = T

class bind[T]:
    def __init__(self, obj: T) -> None:
        self.obj_id: int = id(obj)
        self.obj_name: str = type(obj).__name__
        self.obj: T = obj

    def __get__(self, *_):
        return self.obj

    def __repr__(self) -> str:
        return repr(self.obj)

class DatatypeBlueprint(TypedDict):
    fields: dict[str, Any]


def check_type(Object: dict, blueprint: DatatypeBlueprint) -> bool:
    "returns True if all the types were corrected, False if they were wrong"
    result = True
    if Object.keys() != blueprint["fields"].keys():
        result = False
        return result
    for field in Object:
        data = Object[field]
        if not isinstance(data, blueprint["fields"][field]):
            result = False
    return result
