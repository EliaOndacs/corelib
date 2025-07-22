from abc import ABC, abstractmethod
from typing import Any, Callable, Protocol, runtime_checkable


class Node[T](ABC):
    "(BASE) the base node class with the standard piping protocol"

    __last__: T

    @abstractmethod
    def receive(self, value: Any) -> Any: ...
    @abstractmethod
    def send(self) -> Any: ...

    def __lshift__(self, other: "Node"):
        if not isinstance(other, Node):
            raise TypeError(
                f"the piping protocol is not supported between a 'Node' based object and '{type(other).__name__}'"
            )

        self.receive(other.send())
        return self

    def __rshift__(self, other: "Node"):
        if not isinstance(other, Node):
            raise TypeError(
                f"the piping protocol is not supported between a 'Node' based object and '{type(other).__name__}'"
            )
        other.receive(self.send())
        return other


class DataNode[T](Node[T]):
    "(BASE) a simple data variable node object"

    _value: T
    _lock: bool

    def __init__(self, initial: T) -> None:
        self.value = initial

    @property
    def value(self) -> T:
        "the current value of this node"
        return self._value

    @value.setter
    def value(self, new: T):
        if self._lock == True:
            return
        self._value = new

    def receive(self, value: T):
        self.value = value

    def send(self) -> T:
        return self.value

    def lock(self):
        "lock all 'writes' to this variable node"
        self._lock = True

    def unlock(self):
        "unlock all 'writes' to this variable node"
        self._lock = False


class GeneratorNode[T](Node[T]):
    "(BASE) a type of node that generates data in real-time when piped in"

    params: dict[str, Any]

    def __init__(self, **params) -> None:
        self.params = params

    @abstractmethod
    def generate(self, params: dict[str, Any]) -> T: ...

    def receive(self, value: dict[str, Any]) -> Any:
        self.params = value

    def send(self) -> Any:
        return self.generate(self.params)


class Filter[T](Node[T]):
    "(FUNCTION) will filter out any data that fails its check function"

    checker: Callable[[T], bool]
    isValid: bool

    def __init__(self, checker: Callable[[T], bool]) -> None:
        self.checker = checker

    def receive(self, value: Any) -> Any:
        if self.checker(value) == False:
            self.isValid = False
            return None
        self.isValid = True
        self._last = value

    def send(self) -> Any:
        return self._last


type Checktable[T] = dict[Callable[[T], bool], list[Callable[[T], Any]]]


class Sensor[T](Node[T]):
    "(UTILITY) run callback functions when the the data passes certain check"

    checktable: Checktable[T]

    _last: T | None = None

    def __init__(self, table: Checktable[T]) -> None:
        self.checktable = table

    def set_table(self, table: Checktable[T]):
        self.checktable = table

    def receive(self, value: Any):
        self._last = value
        for checker in self.checktable:
            if checker(value) == True:
                for cb in self.checktable[checker]:
                    cb(value)

    def send(self) -> T | None:
        return self._last


class Modifier[T](Node[T]):
    "(FUNCTION) modify the data using a custom function its given"

    _value: T | None = None
    modifire: Callable[[Any], Any]

    def __init__(self, modifire: Callable[[Any], Any]) -> None:
        self.modifier = modifire

    def receive(self, value: Any) -> Any:
        self.value = self.modifier(value)

    def send(self) -> Any:
        return self.value


