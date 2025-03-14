from functools import partial
from typing import Callable, Protocol
import sys


class Symbol[OptionalTyping]:
    "the Symbol class allows you to construct symbol type which is unique every time."
    data: OptionalTyping | None = None

    def __str__(self):
        return str(self.data) if self.data else "[ object of type symbol ]"


def bind(data: object):
    "bind a object to function"

    def decorator(func):
        return partial(func, data)

    return decorator


class Driver(Protocol):
    def setup(self): ...
    def call(self, func: Callable, *args, **kwargs): ...
    def clear(self): ...
    def data(self, obj: object): ...
    def __call__(self, call: object, *args, **kwds): ...


class TerminalDriver(Driver):
    def setup(self):
        print("started the terminal driver | version: 1.0.0", file=sys.stderr)
        self.ansi_stack: list[str] = []

    def pushAnsi(self, code: str):
        self.ansi_stack.append(code)
        self.data(code)

    def popAnsi(self):
        if len(self.ansi_stack) <= 1:
            self.data("\x1b[0m")
            return ""
        code = self.ansi_stack.pop()
        self.data(self.ansi_stack[-1])
        return code

    def call(self, func: Callable, *args, **kwargs):
        return func(*args, **kwargs)

    def clear(self):
        print("\x1b[H\x1b[2J\r", end="", flush=True)
        return

    def data(self, obj: object):
        print(obj, end="", flush=True)
        return

    def _break(self):
        print("\n", end="", flush=True)
        return

    def __call__(self, call: object, *args, **kwargs):
        if callable(call):
            self.call(call, *args, **kwargs)
        elif call == "clear":
            self.clear()
        elif call == "break":
            self._break()
        elif isinstance(call, str):
            self.data(call)
        else:
            raise RuntimeError(f"unsupported driver call: {call!r}")
