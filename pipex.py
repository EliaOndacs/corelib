"""
a data management and data flow
solution for your python application
this framework gives you a new amazing syntax and
a thinking model for how your data is handled using piping and
different types of node

"""

from abc import ABC, abstractmethod
import random
from typing import Any, Callable, Generator
from math import modf


class Node[T](ABC):
    "(BASE) the base node class with the standard piping protocol"

    __last__: T

    @abstractmethod
    def receive(self, value: Any) -> Any: ...
    @abstractmethod
    def send(self) -> Any: ...

    def __lshift__(self, other: "Node|Any|Callable"):
        if isinstance(other, Node):
            return self.receive(other.send()) or self
        elif callable(other):
            return self.receive(other()) or self

        return self.receive(other) or self

    def __rshift__(self, other: "Node|Any|Callable"):
        if isinstance(other, Node):
            return other.receive(self.send()) or other

        if callable(other):
            return other(self.send())

        return self.receive(other) or self

    def __rrshift__(self, other: Any):
        return self.receive(other) or self

    def __rlshift__(self, other: Any):
        return self.receive(other) or self


class DataNode[T](Node[T]):
    "(BASE) a simple data variable node object"

    _value: T
    _lock: bool = False

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


type Checktable[T, items] = dict[Callable[[T], bool], items]


class Sensor[T](Node[T]):
    "(UTILITY) run callback functions when the the data passes certain check"

    checktable: Checktable[T, list[Callable[[T], Any]]]

    _last: T | None = None

    def __init__(self, table: Checktable[T, list[Callable[[T], Any]]]) -> None:
        self.checktable = table

    def set_table(self, table: Checktable[T, list[Callable[[T], Any]]]):
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
    modifier: Callable[[Any], Any]

    def __init__(self, modifier: Callable[[Any], Any]) -> None:
        self.modifier = modifier

    def receive(self, value: Any) -> Any:
        self.value = self.modifier(value)

    def send(self) -> Any:
        return self.value


class RouterNode[T](Node[T]):

    table: Checktable[T, Node]

    def __init__(self, table: Checktable[T, Node]) -> None:
        self.table = table

    def receive(self, value: Any) -> Any:
        for checker in self.table:
            if checker(value) == True:
                return self.table[checker] << value

    def send(self) -> Any:
        return


class PackNode[T](Node[T]):

    containing: list[T] = []

    def receive(self, value: Any) -> Any:
        self.containing.append(value)

    def send(self) -> Any:
        return self.containing.copy()


class ConditionNode[T](Node[T]):

    checker: Callable[[T], bool]
    value: T | None = None

    def __init__(self, checker: Callable[[T], bool]) -> None:
        self.checker = checker

    def receive(self, value: Any) -> Any:
        if self.checker(value):
            self.value = value
        else:
            self.value = None

    def send(self) -> Any:
        return self.value


class FanNode[T](Node[T]):
    nodes: list[Node]

    def __init__(self, nodes: list[Node]) -> None:
        self.nodes = nodes

    def receive(self, value: Any) -> Any:
        for node in self.nodes:
            node << value

    def send(self) -> Any:
        return


class MemoryNode[T](Node[T]):
    history: list[T]

    def receive(self, value: Any) -> Any:
        self.history.append(value)

    def send(self) -> Any:
        return self.history[-1]


class CloningNode[T](Node[T]):
    value: T
    count: int = 1

    def __init__(self, *, count: int = 1) -> None:
        self.count = count

    def receive(self, value: Any) -> Any:
        self.value = value

    def send(self) -> Any:
        return [self.value] * self.count


class NullNode[T](Node[T]): ...


class LockNode[T](Node[T]):
    _lock: bool
    value: T | None = None

    def lock(self):
        self._lock = True

    def unlock(self):
        self._lock = False

    def receive(self, value: Any) -> Any:
        if self._lock == False:
            self.value = value

    def send(self) -> Any:
        return self.value


class StaticNode[T](Node[T]):
    _value: T

    def __init__(self, constant: T) -> None:
        self._value = constant

    def send(self) -> Any:
        return self._value


class ThresholdNode[T: int](Node[T]):
    threshold: T
    value: T

    def __init__(self, threshold: T) -> None:
        self.threshold = threshold

    def receive(self, value: Any) -> Any:
        self.value = value

    def send(self) -> Any:
        if self.value > self.threshold:
            return self.value
        return None


class NoiseNode[T](Node[T]):
    def send(self) -> Any:
        return random.uniform(-1.0, 0.0)


class ContainerNode[T](Node[T]):
    values: list[T]

    def receive(self, value: Any) -> Any:
        self.values.append(value)

    def send(self) -> Any:
        return self.values.pop()


class AliasNode[T](Node[T]):
    def __init__(self, target: Node[T]) -> None:
        self.target = target

    def receive(self, value: Any) -> Any:
        self.target.receive(value)

    def send(self) -> Any:
        return self.target.send()


class DisconnectNode[T](LockNode[T]):
    signal: T

    def __init__(self, signal: T) -> None:
        self.signal = signal

    def receive(self, value: Any) -> Any:
        a = super().receive(value)
        if value == self.signal:
            self.lock()
            self.value = None
        return a


class TapNode[T](Node[T]):
    value: T

    def receive(self, value: Any) -> Any:
        self.value = value

    def send(self) -> Any:
        return self.value


class EmitNode[T](TapNode[T]):
    callback: Callable[[], Any]

    def __init__(self, callback: Callable[[], Any]) -> None:
        self.callback = callback

    def receive(self, value: Any) -> Any:
        self.callback()
        return super().receive(value)


class FunctionNode[T](Node[T]):
    function: Callable[[T], Any]

    def __init__(self, callback: Callable[[T], Any]) -> None:
        self.function = callback

    def receive(self, value: Any) -> Any:
        self.function(value)
        return

    def send(self) -> Any:
        return


class NodeGroup[T](Node[T]):

    childs: list[Node[T]] = []

    def receive(self, value: Node[T]) -> Any:
        self.childs.append(value)

    def send(self) -> Any:
        return self.childs


class Signal(Node[float]):
    "a powerful data type for activation signals and powers"

    __POWER__: float = 0.0
    __ACTIVATION__: bool = False

    @property
    def power(self) -> float:
        return self.__POWER__

    @power.setter
    def power(self, value: float):
        if (value > 1) or (value < 0):
            raise ValueError(
                f"the power value for a signal object should be between 0 and 99; got {value!r} instead"
            )
        self.__POWER__ = value

    @property
    def activated(self) -> bool:
        return self.__ACTIVATION__

    @activated.setter
    def activated(self, value: bool):
        self.__ACTIVATION__ = value

    def __init__(self, value: float) -> None:
        self.set_float(value)

    def set_float(self, value: float):
        imag, real = modf(value)
        self.activated = real >= 1

        if (imag > 99) or (imag < 0):
            raise ValueError(
                f"the power value {value!r} cannot be used to initiate a signal object; the power value is above 99 or below 0"
            )
        if real < 0:
            raise ValueError(
                f"activation state must be zero or one, got {value.real!r} instead!"
            )
        self.power = imag

    def receive(self, value: float) -> Any:
        self.set_float(value)

    def as_float(self) -> float:
        return eval(f"{'1' if self.activated else '0'}.{str(self.power)[2:]}")

    def send(self) -> float:
        return self.as_float()

    def __repr__(self) -> str:
        return f"SIGNAL(power: {self.power}, activated: {self.activated})"



class Liquid[VT]:
    values: list[VT]

    def __init__(self, *values: VT) -> None:
        self.values = list(values)

    def __iter__(self):
        return self.values

    def reduce(self) -> Generator[VT, None, None]:
        for _ in range(len(self.values)):
            yield self.values.pop()

    def dilution(self, other: "Liquid"):
        self.values.extend(other.values)

    def pour(self, data: VT):
        self.values.append(data)

    def filter(self, func: Callable[[VT], bool]) -> list[VT]:
        extra: list[VT] = []
        new = []
        for item in self.values:
            if func(item):
                new.append(item)
                continue
            extra.append(item)
        self.values = new
        return extra

    @property
    def length(self):
        return len(self.values)



