from typing import Any, TypedDict


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
