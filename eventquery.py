"""
#define _event_queue Queue[Event]

emitEvent(type: object, value: object -> None: ...
queryEvent(type: object) -> EventQuery: ...
clearEvents() -> None: ...

Event[T]:
    type: object
    value: T

EventQuery[T]:
    wait() -> Event[T]: ...
    onEvent(callback: Callable[[Event[T]], None]): ...
    count: int

"""

from dataclasses import dataclass
from typing import Callable


@dataclass
class Event[T]:
    "an event type"
    etype: object
    value: T


type EventCallback[T] = Callable[[Event[T]], None]
"callback function called on an new event"

_event_queue: list[Event] = []
"global queue/list to store all events"

_event_queue_subscribers: list[EventCallback] = []
"global list of subscribers to the event queue/list"


def clearEvents() -> None:
    """
    clear the event queue/list

    ## Note: it won't clear subscribers

    """

    global _event_queue
    _event_queue.clear()


def emitEvent(etype: object, value: object) -> None:
    """
    emit an event with the following event type and value.

    """

    global _event_queue, _event_queue_subscribers
    event = Event(etype, value)
    _event_queue.append(event)
    for callback in _event_queue_subscribers:
        callback(event)


@dataclass
class EventQuery[T]:
    "event query type"

    etype: object

    @property
    def count(self) -> int:
        "the amount of event with this type"

        filterLambda = lambda e: e.etype == self.etype
        filterResult = list(filter(filterLambda, _event_queue))
        return len(filterResult)

    def wait(self) -> Event[T]:
        """
        wait until event and return

        *Warning*: this method is dangerous and can get stuck in a infinite loop if no event was found.
        """

        _wait = True
        while _wait:
            event = _event_queue[-1]
            if event.etype == self.etype:
                _wait = False
        return event  # type: ignore

    def onEvent(self, callback: EventCallback[T]) -> None:
        "add a callback on this event"

        @_event_queue_subscribers.append
        def _(event: Event[T]):
            if event.etype == self.etype:
                callback(event)


def queryEvent(etype: object) -> EventQuery[object]:
    "query a specific type of event"
    return EventQuery(etype)

