from collections.abc import Callable
from typing import Iterable, Literal


def mkmask[T](array: Iterable[T], fn: Callable[[T], bool]) -> list[Literal[0, 1]]:
    """
    makes a binary mask appropriate for the inputted array based on a operation

    Prams:
        array: Iterable[T]
        fn: Callable[[T], bool]
    Returns:
        list[0|1]

    """
    _m: list[Literal[0, 1]] = []  # naming: '_m' for '_mask'
    for item in array:
        if fn(item) == True:
            _m.append(1)
        else:
            _m.append(0)
    return _m


def apply_mask[T](array: Iterable[T], mask: list[Literal[1, 0]]) -> Iterable[T]:
    """
    apply a binary mask to an array

    Prams:
        array: Iterable[T]
        mask: list[0|1]
    Returns:
        Iterable[T]
    """
    new: list[T] = []
    for index, item in enumerate(array):
        if mask[index] == 1:
            new.append(item)
    return new

