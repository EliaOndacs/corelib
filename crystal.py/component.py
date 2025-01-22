from typing import Any, Callable


class Component[*ArgsT]:
    def __init__(self, function: Callable, name: str) -> None:
        self.function = function
        self.name = name

        self.__doc__ = function.__doc__

    def __call__(self, *args: *ArgsT, **kwds: Any) -> Any:
        return self.function(*args, **kwds)
