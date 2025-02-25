"""
python validation library
inspired by zod from @colinhacks

"""

from dataclasses import dataclass, field
from typing import Callable, Optional, Union
import re

class r:

    @dataclass
    class robject:
        structure: dict
        valitation_history: list[bool] = field(default_factory=list)

        def validate(self, data):
            return r.validate(self, data)

    @classmethod
    def _check_type(cls, item, check, key):
        if isinstance(check, type):
            return isinstance(item, check)
        elif isinstance(check, r.robject):
            r.validate(check, item)
            return True
        return check(item, key)

    @classmethod
    def ListType(cls, inner_type: type | Callable | robject):
        def _check(item, key):
            if not isinstance(item, list):
                raise TypeError(
                    f"expected a list for the key {key!r}, got {type(item).__name__!r} instead!"
                )
            for elm in item:
                if not r._check_type(elm, inner_type, key):
                    raise TypeError(f"invalid item in list for key {key!r}")
            return True

        return _check

    @classmethod
    def DictType(
        cls, key_type: type | Callable | robject, value_type: type | Callable | robject
    ):
        def _check(item, key):
            if not isinstance(item, dict):
                raise TypeError(
                    f"expected a dict for the key {key!r}, got {type(item).__name__!r} instead!"
                )
            for k in item:
                v = item[k]
                if not r._check_type(k, key_type, key):
                    raise TypeError(f"invalid `key` in dict for key {key!r}")
                if not r._check_type(v, value_type, key):
                    raise TypeError(f"invalid `value` in dict for key {key!r}")
            return True

        return _check

    @classmethod
    def optional(cls, inner_type: type | Callable | robject):
        def _check(item, key):
            if item == None:
                return True
            if not r._check_type(item, inner_type, key):
                return False
            return True

        return _check

    @classmethod
    def validate(cls, structure: robject, data: dict):
        def visit_node(reference: dict, node: dict):
            if reference.keys() != node.keys():
                raise TypeError(
                    f"expected a data with the following fields: {reference.keys()}, got {node.keys()} instead!"
                )
            for key in reference:
                checker = reference[key]
                real = node[key]
                if isinstance(checker, dict):
                    visit_node(checker, real)
                elif not r._check_type(real, checker, key):
                    raise TypeError(
                        f"didn't expect the type {type(node[key]).__name__!r} for the key {key!r}!"
                    )
            return True

        result = visit_node(structure.structure, data)
        structure.valitation_history.append(result)

    @classmethod
    def constant(cls, value):
        def _check(item, key):
            if item != value:
                raise TypeError(
                    f"expected constant value {value!r} for the key {key!r}"
                )
            return True

        return _check

    @classmethod
    def string_length(cls, min_length: int = 0, max_length: Optional[int] = None):
        def _check(item, key):
            if not isinstance(item, str):
                raise TypeError(
                    f"expected a string for key {key!r}, got {type(item).__name__!r}"
                )
            if len(item) < min_length or (
                max_length is not None and len(item) > max_length
            ):
                raise ValueError(
                    f"length of string for key {key!r} must be between {min_length} and {max_length}"
                )
            return True

        return _check

    @classmethod
    def string_pattern(cls, pattern: str):
        regex = re.compile(pattern)

        def _check(item, key):
            if not isinstance(item, str):
                raise TypeError(
                    f"expected a string for key {key!r}, got {type(item).__name__!r}"
                )
            if not regex.match(item):
                raise ValueError(
                    f"string for key {key!r} does not match pattern {pattern!r}"
                )
            return True

        return _check

    @classmethod
    def number_range(
        cls,
        min_value: Union[int, float] = float("-inf"),
        max_value: Union[int, float] = float("inf"),
    ):
        def _check(item, key):
            if not isinstance(item, (int, float)):
                raise TypeError(
                    f"expected a number for key {key!r}, got {type(item).__name__!r}"
                )
            if item < min_value or item > max_value:
                raise ValueError(
                    f"number for key {key!r} must be between {min_value} and {max_value}"
                )
            return True

        return _check

    @classmethod
    def is_boolean(cls):
        def _check(item, key):
            if not isinstance(item, bool):
                raise TypeError(
                    f"expected a boolean for key {key!r}, got {type(item).__name__!r}"
                )
            return True

        return _check

    @classmethod
    def non_empty_list(cls, inner_type: type | Callable | robject):
        def _check(item, key):
            if not isinstance(item, list) or len(item) == 0:
                raise ValueError(
                    f"expected a non-empty list for key {key!r}, got {type(item).__name__!r}"
                )
            return r.ListType(inner_type)(item, key)

        return _check

    @classmethod
    def unique_items(cls, inner_type: type | Callable | robject):
        def _check(item, key):
            if not isinstance(item, list):
                raise TypeError(
                    f"expected a list for key {key!r}, got {type(item).__name__!r}"
                )
            if len(item) != len(set(item)):
                raise ValueError(f"list for key {key!r} must contain unique items")
            return r.ListType(inner_type)(item, key)

        return _check

