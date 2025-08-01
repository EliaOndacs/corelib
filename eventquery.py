"""
an event base library that adds type smart, events and event query selectors
this modules is also async friendly
"""

from dataclasses import dataclass
from typing import Any, Callable
from queue import Queue
from abc import ABC


@dataclass
class Event[T]:
    "an event type"

    genetic: object
    value: T


type EventCallback[T] = Callable[[Event[T]], None]
"callback function called on an new event"

_event_queue: Queue[Event] = Queue()
"global queue/list to store all events"

_event_queue_subscribers: Queue[EventCallback] = Queue()
"global list of subscribers to the event queue/list"


def clearEvents() -> None:
    """
    clear the event queue/list

    ## Note: it won't clear subscribers

    """

    global _event_queue
    _event_queue = Queue()


def emitEvent(genetic: object, value: object | None = None) -> None:
    """
    emit an event with the following event type and value.

    """

    global _event_queue, _event_queue_subscribers
    event = Event(genetic, value)
    _event_queue.put(event)
    for callback in _event_queue_subscribers.queue:
        callback(event)


@dataclass
class EventQuery[T]:
    "event query type"

    genetic: object

    @property
    def count(self) -> int:
        "the amount of event with this type"

        filterLambda = lambda e: e.genetic == self.genetic
        filterResult = list(filter(filterLambda, _event_queue.queue))
        return len(filterResult)

    def clearEvents(self):
        "clears all the event with this event type"
        global _event_queue

        filterLambda = lambda e: e.genetic != self.genetic
        filterResult = list(filter(filterLambda, _event_queue.queue))
        _event_queue.queue = filterResult

    def wait(self) -> Event[T]:
        """
        wait until event and return

        *Warning*: this method is dangerous and can get stuck in a infinite loop if no event was found.
        """

        _wait = True
        while _wait:
            if len(_event_queue.queue) == 0:
                continue
            event = _event_queue.queue[-1]
            if event.genetic == self.genetic:
                _wait = False
        return event  # type: ignore

    def onEvent(self, callback: EventCallback[T]) -> None:
        "add a callback on this event"

        @_event_queue_subscribers.put
        def _(event: Event[T]):
            if event.genetic == self.genetic:
                callback(event)


def queryEvent(genetic: object) -> EventQuery[Any]:
    "query a specific type of event"
    return EventQuery(genetic)


@dataclass
class Task[T]:
    genetic: object
    value: T | None = None


class EventLoop[T](ABC):
    tasks: list[Task[T]] = []
    alive: bool = True

    def stop(self):
        self.alive = False

    def start(self):
        self.alive = True

    def run(self):
        while self.alive:
            for task in self.tasks:
                emitEvent(task.genetic, task.value)
                self.cycle()

    def remove_task(self, genetic: object):
        self.tasks = [task for task in self.tasks if task.genetic != genetic]

    def mutate_tasks(self, mutator: Callable[[Task], Task]):
        self.tasks = [mutator(task) for task in self.tasks]

    def create_task(self, genetic: object, value: T | None = None):
        self.tasks.append(Task(genetic, value))
        return len(self.tasks) - 1

    def get_task_ids_from_code(self, genetic: object) -> list[int]:
        task_ids = [
            index for index, task in enumerate(self.tasks) if task.genetic == genetic
        ]
        return task_ids

    def get_task_from_id(self, task_id: int) -> Task | None:
        if len(self.tasks) - 1 < task_id:
            return None

        if task_id < 0:
            return None

        return self.tasks[task_id]

    def cycle(self):
        pass
