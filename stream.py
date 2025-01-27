from typing import Callable, Generator

__all__ = ["stream", "read", "close", "setEvent", "dynamic_stream", "exhaust", "new"]

exit_event: int | bool = False
type stream[OutputType] = Generator[OutputType, None, None]


def read[T](inp: stream[T], amount: int = 1) -> list[T]:
    result: list[T] = []
    for _ in range(amount):
        result.append(next(inp))
    return result


def close[T](inp: stream[T]):
    for _ in inp:
        pass


def setEvent(code: int | bool = True):
    global exit_event
    exit_event = code


def dynamic_stream[ReturnType](func: Callable):
    def wrapper(*args, **kwargs) -> stream[ReturnType]:
        while not exit_event:
            yield func(*args, **kwargs)

    return wrapper()


def exhaust[T](inp: stream[T], amount: int = 1):
    for _ in range(amount):
        read(inp)


def new[T](output: list[T]) -> stream[T]:
    yield from output
