"""
# Phelix (a.k.a fire components)
crystal.py version 2
with significant upgrades both in terms of
application architecture and compatibility
"""

from typing import Any, Callable

class Component:
    "a component object"
    state: dict[str, Any] = {}
    "local state of the component"
    function: Callable
    "render logic function passed by the user"
    name: str
    "name of the component"
    app: "Application|None" = None
    "the parent application"

    def __init__(self, function: Callable) -> None:
        self.function = function
        self.name = function.__name__

    def render(self, *args, **kwargs):
        "render the component"
        return self.function(*args, **kwargs)


class Application:
    "a phelix application layer"
    state: dict[str, Any] = {}
    "global state of the app"
    name: str
    "name of the app"
    components: dict[str, Component] = {}
    "components of the app"
    _root: Component | None = None
    "root component of the app"

    def __getattribute__(self, name: str, /):
        try:
            return super().__getattribute__(name)
        except AttributeError:
            if name in self.components:
                return self.components[name]
            else:
                raise

    def __getitem__(self, name: str):
        return self.components[name]

    def __init__(self, name: str) -> None:
        self.name = name

    def component(self, function: Callable) -> Component:
        "create a new component"
        component = Component(function)
        component.app = self
        self.components[component.name] = component
        return component

    def root(self, function: Callable) -> Component:
        "create the root component of the application"
        component = Component(function)
        component.app = self
        self._root = component
        return component

    def render(self):
        "render the application from its root component"
        assert self._root != None, f"{self.name}:root component not defined!"
        return self._root.render()

