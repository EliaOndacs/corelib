from queue import LifoQueue
from typing import Callable


class Event:
    def __init__(self, sender, data) -> None:
        self.sender = sender
        self.data = data


class EventHandler:
    def __init__(self, queue: "EventQueue") -> None:
        self.queue = queue
        self.last_event: Event | None = None
        self.funcs: list[Callable[[Event], None]]
        self.queue.register_listener(self)

    def register(self, handler: Callable[[Event], None]):
        self.funcs.append(handler)

    def _on_event(self, event: Event):
        self.last_event = event
        for handler in self.funcs:
            handler(event)


class EventPump:
    def __init__(self, queue: "EventQueue") -> None:
        self.__queue__ = queue

    async def sendEvent(self, data):
        await self.__queue__.push(Event(self, data))


class EventQueue:
    def __init__(self, maxsize: int = -1):
        self.queue: LifoQueue[Event] = LifoQueue(maxsize)
        self.listeners: list[EventHandler] = []

    def register_listener(self, obj):
        self.listeners.append(obj)

    async def push(self, event: Event):
        for obj in self.listeners:
            obj._on_event(event)
        self.queue.put(
            event
        )  # Warning: this line could block incoming events if no free space found

    async def seek(self) -> Event:
        return self.queue.get()
