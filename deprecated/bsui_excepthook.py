"""
**BaseUi Exception Hook**

import this module to get beautiful error messages
by BaseUi.py

> Note:
> using this module doesn't require importing/packing BaseUi

"""

from typing import Any
from ansi.colour import *  # type: ignore
import sys
from types import TracebackType
from pathlib import Path
from os import get_terminal_size

tw, _ = get_terminal_size()


import pygments
from pygments.lexers import python
from pygments.formatters import TerminalFormatter


class Style:
    def __init__(self, **options: dict[str, Any]):
        self.__data__: dict[str, Any] = options
        self.get = self.__data__.get

    def __repr__(self):
        return f"[object of 'Style' id: {hex(id(self))!r} size: {self.__sizeof__()!r}]"

    def __setitem__(self, key, value):
        self.__data__[key] = value

    def __getitem__(self, key):
        return self.__data__[key]


def ascii_border(text, style: Style | None = None):
    lines = text.split("\n")
    max_len = max(len(line) for line in lines)
    if style:
        border_char = style.get("ascii_border", "-")
        border_vertical_char = style.get("border_vertical_char", "|")
    else:
        border_char = "-"
        border_vertical_char = "|"
    border = border_char * (max_len + 4)
    result = []
    for line in lines:
        bordered_line = (
            f"{border_vertical_char} {line.ljust(max_len)} {border_vertical_char}"
        )
        result.append(bordered_line)
    result.insert(0, border)
    result.append(border)
    return "\n".join(result)


class PrettyLogging:
    def error(self, name, detail, use_stdout: bool = False):
        text = fg.red("ERROR") + " -> " + fg.cyan(name) + ": " + fg.gray(detail)
        if use_stdout == True:
            print(text)
            return
        sys.stderr.write(text + "\n")
        sys.stderr.flush()

    def warn(self, name, detail, use_stdout: bool = False):
        text = fg.yellow("WARN") + " -> " + fg.cyan(name) + ": " + fg.gray(detail)
        if use_stdout == True:
            print(text)
            return
        sys.stderr.write(text + "\n")
        sys.stderr.flush()

    def info(self, name, detail, use_stdout: bool = False):
        text = fg.blue("INFO") + " -> " + fg.cyan(name) + ": " + fg.gray(detail)
        if use_stdout == True:
            print(text)
            return
        sys.stderr.write(text + "\n")
        sys.stderr.flush()


def get_logger() -> PrettyLogging:
    if "global_logger" not in globals():
        globals()["global_logger"] = PrettyLogging()
        return globals()["global_logger"]
    else:
        return globals()["global_logger"]


def bsui_excepthook(
    _type: type[BaseException], err: BaseException, trace: TracebackType | None
):
    def show_trace(trace: TracebackType | None):
        if trace != None:
            print(f"lineN:{trace.tb_lineno}")
            lines = Path(trace.tb_frame.f_code.co_filename).read_text().splitlines()
            new = ""
            i = 0
            for line in lines:
                if i >= (trace.tb_lineno - 5) and i <= (trace.tb_lineno + 5):
                    line = pygments.highlight(
                        line, python.PythonLexer(), TerminalFormatter()
                    )
                    if i + 1 == trace.tb_lineno:
                        new += f"-> {i+1}|" + line
                    else:
                        new += f"   {i+1}|" + line
                i += 1
            print("-" * tw)
            print(new)
            print("-" * tw)
            if trace.tb_next != None:
                show_trace(trace.tb_next)

    show_trace(trace)
    get_logger().error(f"[{_type.__name__}]", repr(err))


sys.excepthook = bsui_excepthook
