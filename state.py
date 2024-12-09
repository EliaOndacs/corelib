from functools import partial
from typing import Callable, Iterable


####################
#      States      #
####################
class State[T]:

    __on_reactivity__: list[Callable] = []

    def __init__(self, default: T | None = None) -> None:
        self.value: T | None = default

    def __repr__(self) -> str:
        return "State[" + str(self.value) + "]"

    def __set_state__(self, new: T | None) -> None:
        self.value = new
        for func in self.__on_reactivity__:
            func(new)


def __setState__[T](state: State, value: T | None):
    state.__set_state__(value)


def __getState__[T](state: State) -> T | None:
    return state.value


def __hookState__[T](state: State, func):
    state.__on_reactivity__.append(func)


def useState[T](default: T | None = None, return_state: bool = False) -> (
    tuple[
        Callable[[], T],
        Callable[[T | None], None],
        Callable[[Callable], None],
    ]
    | tuple[
        State[T], Callable[[T | None], None], Callable[[Callable], None]
    ]
):
    _s = State[T](default)
    _f_set = partial(__setState__, _s)
    _f_get = partial(__getState__, _s)
    _f_hook = partial(__hookState__, _s)
    return (_s if return_state else _f_get), _f_set, _f_hook


def main():

    getCount, *_ = useState(0)

    return


if __name__ == "__main__":
    main()  # pack: ignore
    pass
# end main
