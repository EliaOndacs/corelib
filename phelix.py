"""
# Phelix (a.k.a fire components)
crystal.py version 2
with significant upgrades both in terms of
application architecture and compatibility
"""

from contextlib import contextmanager
from typing import Any, Callable, Literal, cast

_component_stack: list["Component"] = []
"stores the depths of current running components at runtime"


@contextmanager
def useRuntime(component: "Component"):
    """
    (internal hook) it registers a component as running during the runtime.
    allowing for other hooks to use the component object wirelessly
    -> `useComponent`
    """
    global _component_stack
    _component_stack.append(component)
    yield
    _component_stack.pop()
    return


def useComponent(*, index: int = -1) -> "Component":
    "returns the current active component"
    if index < -len(_component_stack) or index >= len(_component_stack):
        raise IndexError("Component index out of range.")
    return _component_stack[index]


class Component:
    "a component object"

    _state: dict[str, Any] = {}
    previous_state: dict[str, Any] = {}
    "previous local state of the component"
    function: Callable
    "render logic function passed by the user"
    name: str
    "name of the component"
    app: "Application|None" = None
    "the parent application"
    _is_mounted: bool = False
    "True if the component has rendered at least once other wise False"
    _reactivity: tuple[Callable[["Component"], None], Callable[["Component"], None]] = (
        lambda _: None,
        lambda _: None,
    )

    @property
    def is_mounted(self) -> bool:
        "True if the component has rendered at least once other wise False"
        return self._is_mounted

    @is_mounted.setter
    def is_mounted(self, s: bool):
        if s == True:
            self._reactivity[0](self)
        self._is_mounted = s

    @property
    def state(self) -> dict[str, Any]:
        "local state of the component"
        return self._state

    @state.setter
    def state(self, new: dict[str, Any]) -> None:
        self.previous_state = self.state.copy()
        self._state = new

    @property
    def is_dirty(self) -> bool:
        "returns wether the component state has changed or not"
        return not (self.previous_state == self._state)

    def useReactivity(
        self,
        update: Callable[["Component"], None],
        mount: Callable[["Component"], None],
    ):
        self._reactivity = (mount, update)

    def __init__(self, function: Callable) -> None:
        self.function = function
        self.name = function.__name__
        self.__doc__ = f"{function.__name__.capitalize()} Component"

    def render(self, *args, **kwargs) -> Any:
        "render the component"
        with useRuntime(self):
            result = self.function(*args, **kwargs)
        self.is_mounted = True
        if self.is_dirty:
            self._reactivity[1](self)
        return result

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.render(*args, **kwds)


def leafComponent(function: Callable) -> Component:
    "create a component without an application"
    component = Component(function)
    component.app = None
    return component


class GlobalStore:
    "(internal) a global state store used for the application"

    def __init__(self):
        self._state: dict[str, Any] = {}
        self._subscribers: dict[str, set[Callable]] = {}

    def get(self, key: str) -> Any:
        "get a state by its name"
        return self._state.get(key)

    def set(self, key: str, value: Any) -> None:
        "set a state value"
        old_value = self._state.get(key)
        if old_value != value:
            self._state[key] = value
            self._notify(key)

    def subscribe(self, key: str, callback: Callable) -> None:
        "add a subscriber callback function on the change of a state by its name"
        if key not in self._subscribers:
            self._subscribers[key] = set()
        self._subscribers[key].add(callback)

    def unsubscribe(self, key: str, callback: Callable) -> None:
        "remove a callback subscriber"
        if key in self._subscribers:
            self._subscribers[key].discard(callback)

    def _notify(self, key: str) -> None:
        for callback in self._subscribers.get(key, []):
            callback()


class Application:
    "a phelix application layer"

    store: GlobalStore
    "the application global state store"
    name: str
    "name of the app"
    components: dict[str, Component] = {}
    "components of the app"
    _root: Component | None = None
    "root component of the app"
    pages: dict[str, Component] = {}
    "contains the other pages of the app"
    active: Component | None = None
    "contains the main component being rendered (defaults to `app._root`)"

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
        self.state = GlobalStore()

    def component(self, function: Callable) -> Component:
        "create a new component"
        component = Component(function)
        component.app = self
        self.components[component.name] = component
        return component

    def route(self, url: str):
        "create a new app route"

        def decorator(function: Callable) -> Component:
            component = Component(function)
            component.app = self
            self.pages[url] = component
            self.active = component
            return component

        return decorator

    def load_route(self, route: str):
        "set the active page to application component at the specified route"

        if not route.startswith("/"):
            raise RuntimeError(f"{self.name}:load_route invalid route {route!r}")

        if (route == "/") or (route == "/root"):
            self.active = self._root
        elif route in self.pages:
            self.active = self.pages[route]
        else:

            self.active = self._root
            return True

        return False

    def root(self, function: Callable) -> Component:
        "create the root component of the application"
        component = Component(function)
        component.app = self
        self._root = component
        self.active = self._root
        return component

    def render(self) -> Any:
        "render the application from its root component"
        assert self.active != None, f"{self.name}:@active component not defined!"
        return self.active.render()


def useState() -> tuple[dict, Callable]:
    "returns the helper functions for reading and writing the component state"
    component = useComponent()  # returns the active component

    def write(state: dict[str, Any], *, ignore_compatibility: bool = False) -> None:
        nonlocal component
        if not ignore_compatibility:
            if not all(key in state for key in component.state.keys()):
                raise RuntimeError(
                    "incompatible state update with the previous component state"
                )
        component.state = state

    return (component.state, write)


def useComponentName() -> str:
    "returns the component name"
    return useComponent().name


def useParentName() -> str:
    "returns the parent component name"
    return useParent().name


def useApp() -> Application | None:
    "returns the current component active application if exists, otherwise returns `None`"
    return useComponent().app


def usePreviousState() -> dict[str, Any]:
    "Returns the previous state of the active component"
    component = useComponent()
    return component.previous_state


def useStateDiff() -> dict[str, tuple[Any, Any]]:
    "return the diff of the current state and the previous state of the component"
    current = useComponent().state
    previous = usePreviousState()
    diffs = {}
    all_keys = set(previous.keys()).union(current.keys())
    for key in all_keys:
        old_val = previous.get(key)
        new_val = current.get(key)
        if old_val != new_val:
            diffs[key] = (old_val, new_val)
    return diffs


def useTemporary[T](initial: T) -> tuple[Callable[[], T], Callable[[T], None]]:
    "creates a temporary state"
    value: T = initial

    def read() -> T:
        nonlocal value
        return value

    def write(new: T):
        nonlocal value
        value = new

    return (read, write)


def useIsMounted():
    "returns True if the component has mounted otherwise False"
    return useComponent().is_mounted


def onMount():
    "like `useIsMounted` but instead it would return True if the component is being mounted"
    return not useIsMounted()


def useEffect(callback: Callable[[], None], dependencies: list[str]) -> None:
    """
    Executes a callback function when specified state keys change.

    **Note**: The callback will not run on the initial mount of the component.
    """
    component = useComponent()
    if not component.is_mounted:
        return
    if not component.is_dirty:
        return

    previous_state = component.previous_state
    current_state = component.state

    changed = False
    for key in dependencies:
        if previous_state.get(key, None) != current_state.get(key, None):
            changed = True
            break

    if changed:
        callback()


def useParent() -> Component:
    "returns the parent component"
    return useComponent(index=-2)


def useStateVar[T](name: str, initial: T) -> tuple[T, Callable[[T], T]]:
    "create a state for the component"
    state, write = useState()

    def writer(new: T) -> T:
        nonlocal state
        write({**state, name: new})
        return new

    return cast(T, state.get(name, initial)), writer


def useRoute(route: str) -> bool:
    "sets the current page/route of the application, returns True if an error occurred"
    app = useApp()
    if app is None:
        raise RuntimeError("useRoute() must be used within an application context")
    return app.load_route(route)


def useGlobalStore() -> GlobalStore:
    "return the current global state store"
    app = useApp()
    if app is None:
        raise RuntimeError(
            "useGlobalStore() must be used within an application context"
        )
    if app.state is None:
        raise RuntimeError("corrupted application instance with no `app.state`!")
    return app.state
