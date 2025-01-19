from dataclasses import dataclass
from typing import Any, Callable, Generator

type ElementStates = dict[str, Any]
type ElementFunction = Callable[[ElementStates], Generator[str, None, None]]


@dataclass
class Element:
    name: str
    states: ElementStates
    default_states: ElementStates
    function: ElementFunction
    cache: str = ""

    def reset(self):
        self.states = self.default_states

    def setAttributes(self, states: ElementStates):
        self.states = states

    def render_loading(self) -> str:
        gen = self.function(self.states)
        result = next(gen)
        self.cache = result
        return result

    def makeInstance(self, states: ElementStates) -> "Element":
        from copy import copy

        r = copy(self)
        r.reset()
        r.setAttributes(states)
        return r

    def render(self) -> str:
        gen = self.function(self.states)
        next(gen)
        return next(gen)

    def __str__(self):
        return self.cache

def component(*, initial_states: ElementStates | None = None):
    if not (initial_states):
        initial_states = {}

    def deco(func: ElementFunction) -> Element:
        name = func.__name__
        return Element(name, initial_states, initial_states, func)

    return deco
