"""
a library that helps you create command prompts
and shell application.

"""

from ansi.colour import *
from typing import Callable, Protocol
from shlex import shlex

__all__ = ["Renderable", "Prompt", "CommandBook", "CommandPrompt"]


class Renderable(Protocol):
    def __str__(self) -> str: ...


type Prompt = list[Renderable]


class CommandBook:
    def __init__(self) -> None:
        self.commands: dict[str, tuple[Callable, str]] = {
            "help": (self.help_command, "show this help message")
        }

    def hook(
        self, func: Callable, description: str | None = None, name: str | None = None
    ):
        if not (name):
            if hasattr(func, "__name__"):
                name = func.__name__
            else:
                raise ValueError(f"cannot hook {func!r}! (requires manual name)")
        if not (description):
            description = func.__doc__
        if not (description):
            description = "[NO DESCRIPTION!]"
        self.commands[name] = (func, description)

    def help_command(self):
        help_msg = "commands: "
        for cmd in self.commands:
            help_msg += f"\n    {cmd}:\n{self.commands[cmd][1]}\n."
        print()
        print(help_msg)


class CommandPrompt:
    def __init__(self, name: str, prompt: Prompt, book: CommandBook) -> None:
        self.name: str = name
        self.prompt: str = self._render_prompt(prompt)
        self.book: CommandBook = book
        self.book.hook(self._exit, f"exit {self.name}", "exit")
        self.cmd: str = ""
        self.arguments: list[str | int] = []
        self.running: bool = True

    def _exit(self):
        self.running = False

    def __call__(self):
        while self.running:
            self._ask()
            cmd: tuple[Callable, str] | None = self.book.commands.get(self.cmd, None)
            if not (cmd):
                print(fg.red("command not found!"))
                continue
            result = cmd[0](*(self.arguments))
            if result:
                print(result)
        print("[exiting]")

    def _render_prompt(self, prompt: Prompt):
        result = ""

        for segment in prompt:
            result += str(segment)

        return result

    def _ask(self):
        stream = input(self.prompt)
        x = shlex(stream, posix=True, punctuation_chars=True)
        self.arguments = []
        i = 0
        for token in x:
            if i == 0:
                self.cmd = token
                i += 1
                continue
            if token.isdigit():
                self.arguments.append(int(token))
                continue
            if token == "true":
                self.arguments.append(True)
                continue
            if token == "false":
                self.arguments.append(False)
                continue
            self.arguments.append(token)
