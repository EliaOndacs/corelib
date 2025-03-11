from typing import Callable
from dataclasses import dataclass, field

_ki: int = -1
def keygen():
    global _ki
    _ki += 1
    return f"Component_{_ki}"


@dataclass
class Component[ReturnType]:
    name: str
    key: str
    state: dict
    func: Callable[["Component"], ReturnType]

    props: dict = field(default_factory=dict)
    _slot_n: int = field(default_factory=int)

    def setState(self, name: str, value: object):
        self.state[name] = value

    def getState(self, name: str) -> object:
        return self.state[name]

    def render(self) -> ReturnType:
        self._slot_n = 0
        result = self.func(self, **self.props)
        return result

    def useState[Type](self, initial: Type) -> tuple[Type, Callable[[Type], Type]]:

        name = f"slot_{self._slot_n}"
        self._slot_n += 1

        if not (name in self.state):
            self.state[name] = initial

        def setMethod(value: Type) -> Type:
            nonlocal name, self
            self.state[name] = value
            return self.state[name]

        return self.state[name], setMethod


def component[T](func: Callable[[Component[T]], T]) -> Component[T]:
    c: Component[T] = Component(func.__name__, keygen(), {}, func)
    c.__doc__ = func.__doc__
    return c


@component
def Counter(this: Component[str]) -> str:
    count, setCount = this.useState(0)
    count2, setCount2 = this.useState(7 - count)
    return f"count<A>: {setCount(count + 1)} count<B>: {setCount2(count2 - 1)}"


def main():

    print(Counter.render())
    print(Counter.render())
    print(Counter.render())
    print(Counter.render())
    print(Counter.render())
    print(Counter.render())

    return


if __name__ == "__main__":
    main()
# end main

