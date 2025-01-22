import time
from typing import Any
import click
from component import Component
from loop import Loop


class Application:
    def __init__(self, main: Component["Application"]) -> None:
        self.loop = Loop()
        self.main = main
        self.storage: dict[str, Any] = {}

    def run(self):
        count = 0
        self.loop.start()
        while self.loop.alive:
            click.clear()
            print(self.main(self), end="", flush=True)
            time.sleep(0.01)
            count = self.loop.__iter__()
        self.loop.kill()
