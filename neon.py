"""
string & styling text library for
terminal based application

this library took a lot of inspiration
from python `rich` library by Will McGugan
so shout out to him and his library.

"""

from dataclasses import dataclass
from functools import wraps
from os import system
import os
import re
from shutil import get_terminal_size
import sys
import threading
import time
from typing import (
    Callable,
    Generator,
    Iterable,
    NamedTuple,
    Literal,
    Optional,
    Protocol,
    runtime_checkable,
    cast,
)
from ansi.colour.rgb import rgb256
from ansi.colour import fx, bg, fg
from pygments.lexer import Lexer
from pygments.lexers import get_lexer_by_name
from pygments.formatters.terminal256 import Terminal256Formatter
from pygments.style import Style as CodeStyle
from pygments import highlight as CodeHighlight
from PIL import Image


@runtime_checkable
class SupportsStr(Protocol):
    def __str__(self) -> str: ...


@runtime_checkable
class SupportsMeasure(Protocol):
    def __neon_measure__(self) -> tuple[int, int]: ...


class _SupportAutoRepr(Protocol):
    def __neon__(self) -> Generator[SupportsStr, SupportsStr | None, None]: ...


class SupportsStrAndAutoRepr(SupportsStr, _SupportAutoRepr, Protocol):
    pass


type TextBorder = tuple[tuple[str, str], tuple[str, str], tuple[str, str, str, str]]
type PaddingRecipe = tuple[int, int, int, int]
type BarStyle = tuple[tuple[str, str], Color, Color, Color]
type TableStyle = tuple[str, str, str]
type SparklineStyle = list[str]
type _AutoReprRenderResult = Generator[SupportsStr, SupportsStr | None, None]
type ScaleStyle = tuple[str, str]
type BreadcrumbStyle = str
type BlockStyle = list[str]


def forge(string: tuple[SupportsStr, SupportsStr]) -> str:
    "forge two strings together"
    string = (str(string[0]), str(string[1]))
    return string[0] + string[1]


def wrap(string: SupportsStr, wrapper: tuple[SupportsStr, SupportsStr]) -> str:
    "wrap the `string` with the `wrapper[0]` at the start and `wrapper[1]` at the end"
    string = str(string)
    wrapper = (str(wrapper[0]), str(wrapper[1]))
    return wrapper[0] + string + wrapper[1]


def merge(string: tuple[SupportsStr, SupportsStr]) -> str:
    "merge two strings together"
    string = (str(string[0]), str(string[1]))
    length = len(string[0]) + len(string[1])
    cursor = [0, 0]
    result = ""
    for i in range(length):
        if i % 2 == 0:
            result += string[0][cursor[0]]
            cursor[0] += 1
        else:
            result += string[1][cursor[1]]
            cursor[1] += 1
    return result


def flip(axis: Literal["x", "y"], string: SupportsStr) -> str:
    "flip the string according to the set axis"
    string = str(string)
    if axis == "y":
        lines = string.splitlines()
        lines.reverse()
        return "\n".join(lines)
    elif axis == "x":
        chars = list(string)
        chars.reverse()
        return flip("y", "".join(chars))


def sort(string: SupportsStr) -> str:
    "sort the characters in the string"
    chars = list(str(string))
    chars.sort()
    return "".join(chars)


def cut(
    string: SupportsStr, position: tuple[int, int]
) -> "tuple[Segment, Segment, Segment]":
    "cut the string from the `position[0]` to `position[1]` and return the three section start, cutted string, end"
    string = str(string)
    start = string[: position[0]]
    cutted = string[position[0] : position[1]]
    end = string[position[1] :]
    return Segment(start), Segment(cutted), Segment(end)


def constrain(content: SupportsStr, width: int, *, reverse: bool = False) -> str:
    """Constrains the content to the specified width."""
    if len(str(content)) < width:
        return str(content)
    if not reverse:
        return str(content)[:width]
    else:
        return str(content)[-width:]


def crop(content: SupportsStr, size: tuple[int, int]) -> str:
    "crop the string to the desired size"
    content = str(content)
    result = ""
    lines = content.splitlines()
    for index in range(min(len(lines), size[1])):
        line = lines[index]
        result += constrain(line, size[0])
        result += "\n"
    return result


def expand(content: SupportsStr, addition: tuple[int, int]) -> str:
    "expand the given content using filler spaces to match the desired measurement"
    content = str(content)
    width, height = addition
    result = ""
    lines = content.splitlines()
    for line in lines:
        result += line + (" " * width) + "\n"
    result += f"{' ' * width}\n" * height
    return result


def replace(
    string: SupportsStr, replace_with: SupportsStr, position: tuple[int, int]
) -> str:
    "replace a range[ `position[0]` : `position[1]` ] inside of a string with a new string"
    start, _, end = cut(string, position)
    return str(start) + str(replace_with) + str(end)


def remove_effects(string: SupportsStr, *, show_where_removed: bool = False) -> str:
    "remove all effects from the string"
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    stripped_text = ansi_escape.sub("(!)" if show_where_removed else "", str(string))
    return stripped_text


def splitchar(line: SupportsStr) -> list[str]:
    "Split a line into a list of characters and controls"
    ansi_escape = re.compile(r"(\x1B\[[0-?]*[ -/]*[@-~]|[^\x1B]+)")
    line = str(line)
    parts = ansi_escape.findall(line)
    segments = [part for part in parts if part]
    chars = []
    for seg in segments:
        if isEscapeCode(seg):
            chars.append(seg)
            continue
        chars.extend(list(seg))
    return chars


def isEscapeCode(code: SupportsStr) -> bool:
    "Check if a string is an escape code"
    return str(code).startswith("\x1b[")


class Character:
    "store a single character/escape code"

    char: str

    def __init__(self, string: SupportsStr = "", *, strip: bool = True) -> None:
        string = str(string)
        if strip == True:
            if len(string) == 0:
                self.char = ""
            else:
                self.char = string[0]
        else:
            self.char = string

    def __repr__(self) -> str:
        return "'" + self.char + "'"

    def __str__(self) -> str:
        return self.char

    def __len__(self):
        return 1

    def __add__(self, other: "SupportsStr|Character"):
        if isinstance(other, SupportsStr):
            return self.char + str(other)
        elif isinstance(other, Character):
            return self.char + other.char

    def __mul__(self, other: int):
        return self.char * other


class Segment:
    "a type of text that does not have a column and rows space"

    text: str

    @classmethod
    def newline(cls) -> "Segment":
        """returns a new line segment"""
        return cls("\n")

    @classmethod
    def segmentation_by_delimiter(
        cls, string: SupportsStr, delimiter: Character
    ) -> list["Segment"]:
        "segmentation by delimiter"
        segments: list[Segment] = []
        string = str(string)
        for seg in string.split(delimiter.char):
            segments.append(cls(seg))
        return segments

    @classmethod
    def segmentation_by_length(
        cls, string: SupportsStr, length: int
    ) -> list["Segment"]:
        "segmentation by length"
        segments: list[Segment] = []
        string = str(string)
        for i in range(0, len(string), length):
            segments.append(cls(string[i : i + length]))
        return segments

    def __init__(self, text: SupportsStr = "") -> None:
        self.text = str(text)

    def __repr__(self) -> str:
        return "'" + self.text + "'"

    def __str__(self) -> str:
        return self.text

    def __len__(self):
        return len(self.text)

    def __add__(self, other: "SupportsStr|Segment|Character"):
        if isinstance(other, SupportsStr):
            return Segment(self.text + str(other))
        elif isinstance(other, Character):
            return Segment(self.text + other.char)
        elif isinstance(other, Segment):
            return Segment(self.text + other.text)


class Line:
    "store a single line with a newline code at the end"

    line: str
    newline: str = "\n"

    def __init__(self, text: SupportsStr = "", *, newline: SupportsStr = "\n") -> None:
        text, newline = str(text), str(newline)
        if len(text.splitlines()) == 0:
            self.line = ""
        else:
            self.line = text.splitlines()[0]
        self.newline = newline

    def __repr__(self) -> str:
        return "'" + self.line + "\\n" + "'"

    def __str__(self) -> str:
        return self.line + self.newline

    def len(self):
        return len(self.line)

    def __add__(self, other: "SupportsStr|Character|Segment|Line"):
        if isinstance(other, SupportsStr):
            return Line(self.line + str(other), newline=self.newline)
        elif isinstance(other, Character):
            return Line(self.line + other.char, newline=self.newline)
        elif isinstance(other, Segment):
            return Line(self.line + other.text, newline=self.newline)
        elif isinstance(other, Line):
            return Multiline(
                (str(self) + str(other)), newline=(self.newline or other.newline)
            )


class Multiline:
    "stores multiple Line `objects`"

    lines: list[Line]

    def __init__(
        self, string: SupportsStr = "", *, newline: SupportsStr = "\n"
    ) -> None:
        string, newline = str(string), str(newline)
        self.lines = [Line(line, newline=newline) for line in string.splitlines()]

    def __repr__(self) -> str:
        return "\n".join([repr(line) for line in self.lines])

    def append(self, line: Line | str):
        if isinstance(line, str):
            self.lines.append(Line(line, newline=self.lines[-1].newline))
        elif isinstance(line, Line):
            self.lines.append(line)

    def insert(self, index: int, line: SupportsStr | Line):
        if isinstance(line, SupportsStr):
            self.lines.insert(index, Line(line, newline=self.lines[index].newline))
        elif isinstance(line, Line):
            self.lines.insert(index, line)

    def remove(self, line: SupportsStr | Line):
        if isinstance(line, SupportsStr):
            self.lines = [l for l in self.lines if l.line != line]
        elif isinstance(line, Line):
            self.lines = [l for l in self.lines if l.line != line.line]

    def __str__(self) -> str:
        return "".join([str(line) for line in self.lines])

    def __add__(self, other: "SupportsStr|Line|Multiline"):
        if isinstance(other, SupportsStr):
            return Multiline(self.__str__() + str(other))
        elif isinstance(other, Line):
            return Multiline(self.__str__() + str(other))
        elif isinstance(other, Multiline):
            return Multiline(str(self) + str(other))


class Control:
    "stores ansi escape codes"

    codes: list[SupportsStr | int]

    def __init__(self, codes: list[SupportsStr | int]) -> None:
        self.codes = codes

    def __repr__(self):
        return ">".join(map(str, self.codes))

    def __str__(self) -> str:
        result = ""
        for code in self.codes:
            if isinstance(code, int):
                result += "\x1b[" + str(code) + "m"
            elif isinstance(code, SupportsStr):
                result += str(code)
        return result

    def __len__(self):
        return 0

    def __add__(self, other: "Control|int|SupportsStr"):
        if isinstance(other, (int, SupportsStr)):
            return Control(self.codes + [other])
        elif isinstance(other, Control):
            return Control(self.codes + other.codes)


class Measurement:
    "store the true and visible measurement of a string"

    string: str | tuple[int, int]

    def __init__(self, string: SupportsStr | SupportsMeasure) -> None:
        if isinstance(string, SupportsMeasure):
            self.string = string.__neon_measure__()
        self.string = str(string)

    @property
    def columns(self) -> int:
        "the true length of a string stored in memory"
        if isinstance(self.string, tuple):
            return self.string[0]
        return len(max(self.string.splitlines(), key=len))

    @property
    def rows(self) -> int:
        "the true length of a string stored in memory"
        if isinstance(self.string, tuple):
            return self.string[1]
        return len(self.string.splitlines())

    @property
    def visible(self) -> tuple[int, int]:
        "the length of the text that will be shown to the user (excludes escape codes)"
        if isinstance(self.string, tuple):
            return self.string
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        stripped_text = ansi_escape.sub("", self.string)
        l = stripped_text.splitlines()
        max_columns = max(len(line) for line in l)
        return max_columns, len(l)


@dataclass
class ScrollableString:

    string: SupportsStr
    view_length: int

    _position: int = 0

    def scroll(self, position: int):
        self._position = position

    def __repr__(self):
        "'INS NOM [VIS] TRM'"
        self.string = str(self.string)
        chars = list(self.string)
        start = self._position
        if start >= len(self.string):
            raise IndexError("start position bigger than string length")
        if start < 0:
            start = 0
        end = start + self.view_length
        if end > len(self.string):
            end = len(self.string) - 1
        chars.insert(start, "[")
        chars.insert(end + 1, "]")
        return "'" + "".join(chars) + "'"

    def __str__(self) -> str:
        self.string = str(self.string)
        start = self._position
        if start >= len(self.string):
            raise IndexError("start position bigger than string length")
        if start < 0:
            start = 0
        end = start + self.view_length
        if end > len(self.string):
            end = len(self.string) - 1
        return self.string[start:end]


@dataclass
class Color:
    "stores real 256 color values"

    red: int
    green: int
    blue: int
    opacity: float
    background: bool = False

    @property
    def rgb(self) -> tuple[int, int, int]:
        "returns the color as a tuple of three integers between 0 and 255"
        return self.red, self.green, self.blue

    @property
    def rgba(self) -> tuple[int, int, int, float]:
        "returns the color as a tuple of four integers and a float between 0 and 1"
        return self.red, self.green, self.blue, self.opacity


@dataclass
class Factor[T]:
    "stores a value for styling"

    unit: str
    value: T


@dataclass
class Style:
    "stores all the different style factors for a renderable to use"

    foreground: Color | None = None
    background: Color | None = None
    padding: PaddingRecipe | None = None
    margin: Factor | None = None


def border(
    string: SupportsStr,
    border: TextBorder = (
        (fg.blue("─"), fg.blue("─")),
        (fg.blue("│"), fg.blue("│")),
        (
            fg.blue("╭"),
            fg.blue("╮"),
            fg.blue("╰"),
            fg.blue("╯"),
        ),
    ),
) -> str:
    """add borders around text (this is a lowlevel function; use `Panel` instead!)"""

    horizontal = list(border[0])
    vertical = list(border[1])
    corners = list(border[2])

    string = str(string)
    lines = string.splitlines()

    m = Measurement(string)
    max_width = m.visible[0]

    border_top = corners[0] + (horizontal[0] * max_width) + corners[1]
    border_bottom = corners[2] + (horizontal[1] * max_width) + corners[3]

    bordered_lines: list[str] = [border_top]
    for line in lines:
        m = Measurement(line)
        bordered_lines.append(
            f"{vertical[0]}{line}{' '*((max_width)-m.visible[0])}{vertical[1]}"
        )
    bordered_lines.append(border_bottom)

    return "\n".join(bordered_lines)


def padding(
    string: SupportsStr,
    amount: PaddingRecipe = (0, 0, 0, 0),
    style: Style | None = None,
) -> str:
    "add padding to the string"
    # Split the input into lines
    lines = str(string).splitlines()
    m = Measurement(string)
    max_width = m.visible[0]
    if (style) and (style.padding):
        left, bottom, top, right = style.padding
    else:
        left, bottom, top, right = amount

    # Add left and right padding to each line
    padded_lines = [
        f"{' ' * left}{line}{' ' * (right + max_width - len(stripped_line))}"
        for line, stripped_line in zip(lines, str(string).splitlines())
    ]

    # Add top and bottom padding
    top_padding = [" " * (max_width + left + right)] * top
    bottom_padding = [" " * (max_width + left + right)] * bottom

    # Combine everything
    final_lines = top_padding + padded_lines + bottom_padding
    return "\n".join(final_lines)


def colortext(content: SupportsStr, style: Style, *, reset: bool = True) -> str:
    "add color to the string"
    codes = []
    if isinstance(style.foreground, Color):
        codes.append(rgb256(*style.foreground.rgb))
    if isinstance(style.background, Color):
        codes.append(rgb256(*style.background.rgb, bg=True))
    return forge((str(Control(codes)), str(content))) + ("\x1b[0m" if reset else "")


class Projection:
    "a pre-allocated 2D buffer"

    _width: int
    _height: int
    _content: list[list[str]]

    def __init__(self, content: list[list[str]], width: int, height: int):
        self._width = width
        self._height = height
        self._content = content

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def content(self) -> list[list[str]]:
        return self._content

    def __neon__(self):
        for row in self.content:
            for cell in row:
                yield cell
            yield "\n"

    def __str__(self) -> str:
        return str(useAutoRepr(self))

    def __repr__(self) -> str:
        return f"Projection(width={self.width}, height={self.height})"


def percentage(value: int | float, max: int) -> int | float:
    "calculate percentage of value in max"
    return (value / max) * 100


def rem(value: int | float) -> int | float:
    return value * 16


class Canvas:
    "a pre-allocated 2D buffer for multi-layer string editing"

    width: int
    height: int
    buff: list[list[Character]]

    def __init__(self, width: int, height: int, filler: str = " ") -> None:
        self.width = width
        self.height = height
        self.buff = [
            [Character(filler) for _ in range(self.width)] for _ in range(self.height)
        ]

    def recalculate_buffer_length(self):
        "Recalculate the length of the buffer to match the width of the canvas"
        if self.height > len(self.buff):
            for _ in range(len(self.buff), self.height):
                self.buff.append([Character(" ") for _ in range(self.width)])
        elif self.height < len(self.buff):
            self.buff = self.buff[: self.height]

        for row in self.buff:
            if self.width > len(row):
                row.extend([Character(" ") for _ in range(len(row), self.width)])
            elif self.width < len(row):
                row[:] = row[: self.width]

    def setcol(self, char: str, row: int, col: int):
        if (row < 0) or (row >= self.height) or (col < 0) or (col >= self.width):
            raise IndexError(
                f"Character position ({row}, {col}) exceeds buffer dimensions ({self.height}, {self.width})"
            )
        self.buff[row][col] = Character(char, strip=not isEscapeCode(char))

    def project(self, content: SupportsStr, *, x: int = 0, y: int = 0):
        "project a string onto the canvas at the specified position"
        # TODO: this code is so problematic i can't even begin to explain why
        # TODO: please fix this for god sake
        content = str(content)
        for i, row in enumerate(content.splitlines()):
            for j, char in enumerate(splitchar(row)):
                if (
                    (i + y < 0)
                    or (i + y >= self.height)
                    or (j + x < 0)
                    or (j + x >= self.width)
                ):
                    raise IndexError(
                        f"Character position ({i + y}, {j + x}) exceeds buffer dimensions ({self.height}, {self.width})"
                    )
                self.setcol(char, i + y, j + x)

    def render(self) -> Projection:
        "render the canvas to a projection"
        return Projection(
            content=[[c.char for c in row] for row in self.buff],
            width=self.width,
            height=self.height,
        )


class TerminalDriver:

    @property
    def width(self) -> int:
        "the width of the terminal"
        return get_terminal_size().columns

    @property
    def height(self) -> int:
        "the height of the terminal"
        return get_terminal_size().lines

    @property
    def fhandle(self) -> tuple[int, int, int]:
        "returns the file handle to stdout, stdin, stderr"
        return sys.stdout.fileno(), sys.stdin.fileno(), sys.stderr.fileno()

    def clear(self):
        "clear the terminal screen"
        system("cls" if os.name == "nt" else "clear")

    def settitle(self, title: SupportsStr):
        "set the terminal title"
        self.stdout(f"\033]2;{title}\007")

    def alternative_screen(self, flag: bool = True):
        "enable the alternative screen"
        if flag:
            self.stdout("\033[?1049h")
        else:
            self.stdout("\033[?1049l")

    def cursor(self, flag: bool = False):
        "toggle the cursor on the terminal"
        if flag:
            self.stdout("\033[?25h")
        else:
            self.stdout("\033[?25l")

    def goto(self, row: int, col: int):
        "move the cursor to the specified position"
        self.stdout(f"\033[{row};{col}H")

    def store(self):
        "store the cursor position"
        self.stdout("\033[s")

    def restore(self):
        "restore the cursor position"
        self.stdout("\033[u")

    def clear_line(self):
        "clear the current line"
        self.stdout("\r\033[K")

    def home(self):
        "move the cursor to the home position"
        self.goto(0, 0)

    def bell(self):
        "ring the terminal bell"
        self.stdout("\a")

    def mode(self, code: int):
        "set the terminal mode"
        self.stdout(f"\033[{code}m")

    def stdout(self, data: SupportsStr):
        sys.stdout.write(str(data))
        sys.stdout.flush()

    def stderr(self, data: SupportsStr):
        sys.stderr.write(str(data))
        sys.stderr.flush()

    def stdin(self) -> str:
        return sys.stdin.read()


class Panel:
    "draws a border around its contents"

    def __init__(
        self,
        content: SupportsStr,
        *,
        title: str | None = None,
        subtitle: str | None = None,
        width: int | None = None,
        padding: PaddingRecipe | None = None,
        border_style: TextBorder | None = None,
        style: Style | None = None,
    ) -> None:
        self.content = content
        self.style = style
        self.width = width
        self.title = title
        self.subtitle = subtitle
        self.padding = padding
        self.border_style = border_style

    def __str__(self) -> str:
        content = self.content
        if self.width is not None:
            content = constrain(content, self.width)
        if self.padding is not None:
            content = padding(content, self.padding, style=self.style)
        content = border(
            content,
            (
                self.border_style
                if self.border_style
                else (
                    ("─", "─"),
                    ("│", "│"),
                    (
                        "╭",
                        "╮",
                        "╰",
                        "╯",
                    ),
                )
            ),
        )
        if self.title is not None:
            m = Measurement(content)
            c = Canvas(m.columns, m.rows)
            c.project(content)  # <- here
            title = self.title
            if len(self.title) > m.columns:
                title = ""
            c.project(" " + title + " ", x=3)
            content = str(c.render())  # <- here
        if self.subtitle is not None:
            m = Measurement(content)
            c = Canvas(m.columns, m.rows)
            c.project(content)
            subtitle = self.subtitle
            if len(self.subtitle) >= m.columns:
                subtitle = ""
            c.project(
                " " + subtitle + " ", x=m.columns - 4 - len(subtitle), y=m.rows - 1
            )
            content = str(c.render())
        return content


class ProgressBar:
    "colorful progress bar"

    def __init__(
        self,
        total: int = 100,
        completed: int = 0,
        width: int = 10,
        bar_style: BarStyle | None = None,
    ):
        self.total = total
        self.completed = completed
        self.width = width
        self.bar_style = bar_style

    def update(self, value: int):
        if self.completed == self.total:
            return
        self.completed += value

    def reset(self):
        self.completed = 0

    def __str__(self) -> str:
        content = ""
        if self.bar_style:
            off_code = self.bar_style[1]
            on_code = self.bar_style[2]
            end_code = self.bar_style[3]
            unfinished, finished = self.bar_style[0]
        else:
            off_code = Color(33, 33, 33, 1)
            on_code = Color(232, 16, 81, 1)
            end_code = Color(124, 232, 16, 1)
            unfinished, finished = ("━", "━")
        on_style = Style(foreground=on_code)
        off_style = Style(foreground=off_code)
        end_style = Style(foreground=end_code)
        number = (self.completed * (self.width + 1)) // self.total
        off = colortext(unfinished, style=off_style)
        on = colortext(finished, style=on_style)
        if self.completed >= self.total:
            on = colortext(finished, style=end_style)
        content += f"{on * number}{off * (self.width - number)}"
        return content


class Animation:
    "static animation"

    def __init__(self, frames: list[SupportsStr], *, loop: bool = False) -> None:
        self.frames = frames
        self.index = 0
        self.loop = loop

    def update(self):
        self.index = (
            ((self.index + 1) % len(self.frames)) if self.loop else (self.index + 1)
        )

    def __next__(self):
        self.update()
        return str(self)

    def __iter__(self):
        return self.frames

    def __str__(self) -> str:
        return str(self.frames[self.index])


class Live:
    "live display content using threads"

    def __init__(
        self,
        content: SupportsStr,
        *,
        transient: bool = False,
        refresh_per_second: int = 4,
    ) -> None:
        self.content = content
        self._lock = threading.Lock()
        self.started = False
        self.transient = transient
        self.refresh_per_second = refresh_per_second
        self.driver = TerminalDriver()

    def update(self, renderable: SupportsStr):
        with self._lock:
            self.content = renderable

    def start(self):
        with self._lock:
            if self.started:
                return
            self.started = True

        refresh_interval = 1 / self.refresh_per_second

        while True:
            with self._lock:
                if not self.started:
                    break
                self.driver.clear_line()
                self.driver.stdout(str(self.content))
            time.sleep(refresh_interval)

        if self.transient:
            self.driver.clear_line()
        else:
            self.driver.stdout("\n")

    def stop(self):
        with self._lock:
            self.started = False

    def __enter__(self):
        threading.Thread(target=self.start).start()
        return self

    def __exit__(self, *exc_info):
        self.stop()


class Status:
    "display work progress with a spinner"

    def __init__(
        self,
        progress: SupportsStr = "loading...",
        *,
        spinner: list[str] = [".  ", ".. ", "...", " ..", "  .", "   "],
        transient: bool = False,
        refresh_per_second: int = 4,
    ) -> None:
        self.progress = str(progress)
        self.spinner = spinner
        self._lock = threading.Lock()
        self.started = False
        self.transient = transient
        self.refresh_per_second = refresh_per_second
        self.driver = TerminalDriver()

    def start(self):
        with self._lock:
            if self.started:
                return
            self.started = True

        spinner = Animation(self.spinner, loop=True)  # type: ignore
        interval = 1 / self.refresh_per_second
        with Live(str(spinner), transient=True) as liv:
            while True:
                with self._lock:
                    if not self.started:
                        break
                    spinner.update()
                    liv.update(f"{str(spinner)} {self.progress}")
                time.sleep(interval)

        if self.transient:
            self.driver.clear_line()
        else:
            self.driver.stdout("\n")

    def stop(self):
        with self._lock:
            self.started = False

    def __enter__(self):
        threading.Thread(target=self.start).start()
        return self

    def __exit__(self, *exc_info):
        self.stop()


def rule(
    character: SupportsStr | Character,
    width: int,
    *,
    title: str | None = None,
    newline: bool = True,
):
    "rule with the given character and width and a title"
    _character = str(character).replace("\n", " ").expandtabs(4)
    char_len = Measurement(_character).visible[0]
    content = str(Line(str(_character) * ((width // char_len)), newline=""))
    if title:
        m = Measurement(content)
        c = Canvas(width, 1)
        c.project(content)
        c.project(" " + title + " ", x=(m.visible[0] // 2 - (len(title) // 2) - 1))
        content = str(c.render())
    return content + ("\n" if newline else "")


class Table:
    "a table with a header and rows"

    def __init__(
        self, *headers: SupportsStr, table_style: TableStyle = ("│", "─", "┼")
    ) -> None:
        self.headers = tuple(map(str, headers))
        self.data: list[list[str]] = []
        self.style = table_style

    def add_row(self, *columns: str) -> None:
        self.data.append(list(columns))

    def __str__(self) -> str:
        column_widths = [
            max(len(str(item)) for item in col) for col in zip(self.headers, *self.data)
        ]

        row_format = f" {self.style[0]} ".join(
            f"{{:<{width}}}" for width in column_widths
        )

        header_row = row_format.format(*self.headers)
        separator = (self.style[1] + self.style[2] + self.style[1]).join(
            self.style[1] * width for width in column_widths
        )

        data_rows = "\n".join(row_format.format(*row) for row in self.data)

        return (
            f"{header_row}\n{separator}\n{data_rows}"
            if self.data
            else f"{header_row}\n{separator}"
        )


class Sparkline:
    def __init__(
        self,
        data: list[float],
        *,
        sparkline_style: SparklineStyle = [
            fg.blue("▁"),
            fg.cyan("▂"),
            fg.green("▃"),
            fg.brightgreen("▄"),
            fg.yellow("▅"),
            fg.brightmagenta("▆"),
            fg.red("█"),
        ],
    ):
        self.data = data
        self.sparkline_style = sparkline_style

    def feed(self, value: float):
        "add new point to data"
        self.data.append(value)

    def __str__(self) -> str:
        content = ""
        min_d = min(self.data)
        max_d = max(self.data)
        range_d = max_d - min_d if max_d != min_d else 1
        for value in self.data:
            index = int((value - min_d) / range_d * (len(self.sparkline_style) - 1))
            content += self.sparkline_style[index]
        return content


class Group:
    "a group of renderables that render as one renderable instead"

    def __init__(self, *renderables: SupportsStr) -> None:
        self.renderables = renderables

    def __str__(self) -> str:
        content = Segment("")
        for renderable in self.renderables:
            content += Segment(str(renderable))
        return str(content)


def group(func: Callable[..., Iterable[SupportsStr]]):
    "a decorator that groups the output of a function into a single renderable"

    @wraps
    def wrapper(*args, **kwargs):
        return Group(*func(*args, **kwargs))

    return wrapper


def joingen(func: Callable[..., Generator[SupportsStr, SupportsStr | None, None]]):
    "a decorator that joins the output of a function into a single renderable"

    @wraps(func)
    def wrapper(*args, **kwargs) -> str:
        renderables = list(func(*args, **kwargs))
        return str(Group(*renderables))

    return wrapper


def useAutoRepr(obj: _SupportAutoRepr) -> SupportsStr:
    if not hasattr(obj, "__neon__"):
        raise TypeError(f"autorepr only supports classes that support __neon__")

    return joingen(obj.__neon__)()


def autorepr(func: Callable[..., Generator[SupportsStr, SupportsStr | None, None]]):
    """Autorepr decorator for functions that return generators."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return joingen(func)(*args, **kwargs)

    return wrapper


class Screen:
    "renders the renderables within the whole terminal screen and crop the extra"

    def __init__(self, *renderables: SupportsStr):
        self.renderable = Group(*renderables)
        self.driver = TerminalDriver()

    def __str__(self):
        width, height = self.driver.width, self.driver.height
        c = Canvas(width, height)
        c.project(crop(self.renderable, (width, height)))
        return str(c.render())


class Paginator:
    "shows the current set page number"

    page: int
    total: int

    def __init__(self, total: int, *, page: int = 1) -> None:
        self.total = total
        self.page = page

    def __neon__(self) -> Generator[SupportsStr, SupportsStr | None, None]:
        yield "<" if self.page > 1 else "["
        yield f" {self.page}/{self.total} "
        yield ">" if self.page < self.total else "]"

    def __str__(self) -> str:
        return str(useAutoRepr(self))


class ScaleBar:
    "a scale bar for a plot."

    def __init__(
        self,
        total: int = 100,
        *,
        completed: int = 0,
        width: int = 10,
        scale_style: ScaleStyle = (fg.cyan("█"), fg.cyan("░")),
    ) -> None:
        self.total = total
        self.completed = completed
        self.width = width
        self.scale_style = scale_style

    def update(self, amount: int = 1):
        self.completed += amount

    def reset(self):
        self.completed = 0

    def __neon__(self) -> Generator[SupportsStr, SupportsStr | None, None]:
        if self.completed == self.total:
            yield f"{self.scale_style[0]*self.width}"
            return
        bars = (self.completed * self.width) // self.total
        yield Segment(self.scale_style[0] * bars)
        yield Segment(self.scale_style[1] * (self.width - bars))

    def __str__(self) -> str:
        return str(useAutoRepr(self))


class Breadcrumb:
    "a breadcrumb to display a list of items in order of their hierarchy"

    def __init__(
        self,
        items: list[SupportsStr],
        *,
        breadcrumb_style: BreadcrumbStyle = fg.cyan(" / "),
    ) -> None:
        self.items = items
        self.breadcrumb_style = breadcrumb_style

    def __neon__(self):
        last = len(self.items) - 1
        for index, item in enumerate(self.items):
            yield Segment(item)
            if index != last:
                yield Segment(self.breadcrumb_style)

    def __str__(self) -> str:
        return str(useAutoRepr(self))


@autorepr
def header(name: SupportsStr):
    "header title component"
    driver = TerminalDriver()

    yield rule(fg.brightblue("─"), driver.width)
    yield rule(" ", driver.width, title=str(name).capitalize(), newline=False)
    yield rule(fg.brightblue("─"), driver.width)


@autorepr
def listview(items: list[SupportsStr], *, items_prefix: str = "- "):
    """A list view widget that displays a list of items."""
    for item in items:
        yield Segment(items_prefix)
        yield item
        yield Segment.newline()


@autorepr
def strong(content: SupportsStr):
    """A strong text widget that displays content in a bold font."""
    yield fx.bold(str(content))


@autorepr
def highlight(content: SupportsStr):
    """Highlight a specific content with a yellow background."""
    yield fx.inverse(str(content))


@autorepr
def strike(content: SupportsStr):
    """A strike-through text widget that displays a string with a strike-through effect."""
    yield fx.crossed_out(str(content))


@autorepr
def blink(content: SupportsStr):
    """A blink effect that blinks the content on and off."""
    yield fx.blink(str(content))


@autorepr
def link(text: SupportsStr, url: str):
    """A link widget that displays a link to the given URL."""
    content = fx.underline(fg.cyan(str(text)))
    yield f"\033]8;;{url}\033\\{content}\033]8;;\033\\"


class Syntax:
    "a component to display code with syntax highlighting and line number"

    def __init__(
        self,
        code: SupportsStr,
        lexer: Lexer | str,
        *,
        theme: str | CodeStyle = "monokai",
    ):
        self.code = code
        if isinstance(lexer, str):
            self.lexer = get_lexer_by_name(lexer)
        else:
            self.lexer = lexer
        self.formatter = Terminal256Formatter(style=theme)

    def __neon__(self):
        content = str(self.code)
        content = CodeHighlight(content, self.lexer, self.formatter)
        lines = content.splitlines()
        space_width = 4
        for index, line in enumerate(lines):
            if len(str(index + 1)) >= space_width:
                space_width += 2
            yield Segment(" " * (space_width - len(str(index + 1))))
            yield Segment(index + 1)
            yield Segment("│")
            yield line
            yield Segment.newline()

    def __str__(self) -> str:
        return str(useAutoRepr(self))


class VerticalContainer:
    "renders multiple renderables in a vertical order"

    def __init__(self, *renderables: SupportsStr) -> None:
        self.renderables = renderables

    def __neon__(self):
        for renderable in self.renderables:
            yield str(renderable)
            yield "\n"

    def __str__(self) -> str:
        return str(useAutoRepr(self))


class Map:
    "renders a 2D binary map into renderable using the `BlockStyle` guide"

    def __init__(
        self,
        shape: list[list[int]],
        *,
        block_style: BlockStyle = [bg.white("██"), "  "],
    ) -> None:
        self.shape = shape
        self.block_style = block_style

    def __neon__(self):
        for row in self.shape:
            for col in row:
                yield self.block_style[col]
            yield "\n"

    def __str__(self) -> str:
        return str(useAutoRepr(self))


@autorepr
def pixelimage(
    path: str,
    *,
    width: Optional[int] = None,
    height: Optional[int] = None,
    texture: Optional[SupportsStr] = None,
):
    "renders an image into terminal columns"
    img = Image.open(path)
    img = img.convert("RGB")
    if width == None:
        width = img.width
    if height == None:
        height = img.height
    img = img.resize((width or 0, height or 0))
    for y in range(height or 0):
        for x in range(width or 0):
            rgb = cast(tuple[int, int, int], img.getpixel((x, y)))
            yield rgb256(*rgb, True) + (str(texture) if texture else " ")
    yield "\x1b[0m"


class rect(NamedTuple):
    "stores a region from x,y with the width, height"

    width: int
    height: int
    x: int
    y: int

    def __str__(self) -> str:
        return str(useAutoRepr(self))

    def __neon__(self):
        yield f"x: {self.x} y: {self.y}\n"
        for _ in range(self.height):
            for _ in range(self.width):
                yield "#"
            yield "\n"


@autorepr
def percentageCounter(value: float | int, max: float | int):
    "display a percentage based counter with an '%' mark next to it [Note: the out of hundred measure will be calculated automatically]"
    yield ((value * 100) // max)
    yield "%"
