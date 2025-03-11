from functools import partial


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

