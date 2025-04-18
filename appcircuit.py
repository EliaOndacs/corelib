from contextlib import contextmanager
from typing import Protocol
import click, sys


def create_input_handler():
    if sys.platform == "win32":
        import msvcrt

        return msvcrt.getch
    else:
        import termios

        def getch(self):
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                ch = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            return ch

        return getch


_cursor = True


def toggle_cursor():
    global _cursor
    if _cursor:
        _cursor = False
        print("\033[?25l", end="", flush=True)
    else:
        _cursor = True
        print("\033[?25h", end="", flush=True)


@contextmanager
def cursor():
    global _cursor
    _cursor = False
    toggle_cursor()
    yield
    _cursor = True
    toggle_cursor()


def notify(text: str):
    print("\033[999;1H", end="")
    print(text, flush=True, end="")
    click.pause("")
    print("\r", end="", flush=True)
    return


def prompt(text: str) -> str:
    print("\033[999;1H", end="")
    with cursor():
        value = input(text)
    return value


def runApp(app: "App"):
    global _cursor
    input_handler = create_input_handler()
    print("\033[?1049h", end="", flush=True)
    _cursor = True
    toggle_cursor()
    app.init()
    while app.alive:
        click.clear()
        print(end="", flush=True)
        app.draw()
        app.update(input_handler())
    _cursor = False
    toggle_cursor()
    print("\033[?1049l", end="", flush=True)


class App(Protocol):
    alive: bool

    def init(self): ...
    def update(self, key: bytes): ...
    def draw(self): ...

