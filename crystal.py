from typing import Callable, Literal
from dataclasses import dataclass, field
from functools import wraps

_ki: int = -1


class StateError(Exception): ...


def keygen():
    global _ki
    _ki += 1
    return f"Component_{_ki}"


@dataclass
class Component[ReturnType]:
    name: str
    key: str
    state: dict
    func: Callable[..., ReturnType]

    props: dict = field(default_factory=dict)
    _is_mounted: bool = False
    _slot_n: int = field(default_factory=int)
    _previous_state: dict = field(default_factory=dict)

    def __hash__(self) -> int:
        return hash(self.key)

    def setState(self, name: str, value: object):
        self._previous_state[name] = self.state.get(name)
        self.state[name] = value
        self.componentDidStateUpdate(name, value)

    def getState(self, name: str) -> object:
        try:
            return self.state[name]
        except KeyError:
            raise StateError(
                f"the state {name!r} not found for the component {self.name!r}"
            )

    def getPrevious(self, name: str) -> object:
        try:
            return self._previous_state[name]
        except KeyError:
            raise StateError(
                f"the state {name!r} has just initialised or do not exists for the component {self.name!r}"
            )

    def componentDidMount(self):
        """Called after the component is mounted."""
        pass

    def componentDidUpdate(self):
        """Called after the component is updated."""
        pass

    def componentWillUnmount(self):
        """Called before the component is unmounted."""
        pass

    def componentDidStateUpdate(self, name: str, value: object):
        """Called when a state in a component is being updated."""

    def render(self, children) -> ReturnType:
        self._slot_n = 0
        result = self.func(self, *children, **self.props)
        if self._is_mounted == True:
            self.componentDidUpdate()  # Call after rendering
        if self._is_mounted == False:
            self.componentDidMount()  # Call when the component is mounted
            self._is_mounted = True
        return result

    def export(self, obj: object):
        self.__dict__[obj.__name__] = obj  # type: ignore

    def exportas(self, obj: object, name: str):
        self.__dict__[name] = obj

    def useState[Type](self, initial: Type) -> tuple[Type, Callable[[Type], Type]]:

        name = f"slot_{self._slot_n}"
        self._slot_n += 1

        if not (name in self.state):
            self.state[name] = initial

        def setMethod(value: Type) -> Type:
            nonlocal name, self
            self._previous_state[name] = self.state.get(name)
            self.state[name] = value
            self.componentDidStateUpdate(name, value)
            return self.state[name]

        return self.state[name], setMethod

    def useStateName(self):
        return f"slot_{self._slot_n-1}"

    def __call__(self, *children, **kwargs) -> ReturnType:
        self.props.update(kwargs)
        return self.render(children)

    def bindLifecycleEvent(
        self,
        event: Literal[
            "componentMount", "componentUnmount", "componentUpdate", "stateUpdate"
        ],
        callback: Callable,
    ):
        """
        Binds a callback function to a specific lifecycle event of the component.

        Args:
            event (Literal): The lifecycle event to bind the callback to.
                Can be one of the following:
                - "componentMount": Called when the component is mounted.
                - "componentUnmount": Called when the component is about to unmount.
                - "componentUpdate": Called after the component is updated.
                - "stateUpdate": Called when a state variable is updated.
            callback (Callable): The function to be called when the specified event occurs.
        """
        match event:
            case "stateUpdate":
                setattr(self, "componentDidStateUpdate", callback)
            case "componentMount":
                setattr(self, "componentDidMount", callback)
            case "componentUnmount":
                setattr(self, "componentWillUnmount", callback)
            case "componentUpdate":
                setattr(self, "componentDidUpdate", callback)


def createComponent[T](func: Callable[..., T]) -> Component[T]:
    c: Component[T] = Component(func.__name__, keygen(), {}, func)
    c.__name__ = func.__name__  # type: ignore
    c.__doc__ = func.__doc__
    return c


def mkinstance[T](component: Component[T]) -> Component[T]:
    c: Component[T] = Component(
        component.name, keygen(), component.props, component.func
    )
    c.__name__ = component.func.__name__  # type: ignore
    c.__doc__ = component.func.__doc__
    return c


# state management


class StateStore:
    def __init__(self, initial_state):
        self.state = initial_state
        self.subscribers = []

    def reducer(self, func):
        self.reducer_func = func

    def dispatch(self, action):
        self.state = self.reducer_func(self.state, action)
        self.notify_subscribers()

    def select(self, key):
        return self.state.get(key), lambda action: self.dispatch(action)

    def notify_subscribers(self):
        for subscriber in self.subscribers:
            subscriber(self.state)

    def subscribe(self, callback):
        self.subscribers.append(callback)
