"""
**BaseUi**

the base ui library for a centralized theme cli ui among SysCoreutil & SysEnv

"""

from dataclasses import dataclass
from typing import (
    Any,
    Generator,
    Iterable,
    Literal,
    Protocol,
    Callable,
    runtime_checkable,
)
from warnings import deprecated
from ansi.colour import *  # type: ignore
from enum import StrEnum
import sys, re


@runtime_checkable
class Renderable(Protocol):
    def __str__(self) -> str: ...


class Component(Renderable):

    def __init__(self, states: dict[str, Any]) -> None:
        self.states = states

    def compose(self) -> Generator["Renderable|Component"]:
        yield from ()

    @property
    def package(
        self,
    ) -> Generator["Renderable|Component", None, None]:
        yield from self.compose()

    def render(self):
        result = ""
        for item in self.package:
            if isinstance(item, Renderable):
                result += str(item)
            elif isinstance(item, Component):
                result += str(item)

        return result

    def __str__(self):
        return self.render()


class codes(StrEnum):
    CLEAR = "\x1b[2J"
    UP = "\x1b[A"
    HOME = "\x1b[H"


class Style:
    "style object for all styles of all components"

    def __init__(self, options: dict[str, Any]):
        self.__data__: dict[str, Any] = options
        self.get = self.__data__.get

    def __repr__(self):
        return f"[object of 'Style' id: {hex(id(self))!r} size: {self.__sizeof__()!r}]"

    def __setitem__(self, key, value):
        self.__data__[key] = value

    def __getitem__(self, key):
        return self.__data__[key]


def mergeStyles(style_A: Style, style_B: Style):
    return Style({**style_A.__data__, **style_B.__data__})


class Setting:
    "setting object for all configuration of all components"

    def __init__(self, options: dict[str, Any]) -> None:
        self.__data__: dict[str, Any] = options
        self.get = self.__data__.get

    def __repr__(self):
        return (
            f"[object of 'Setting' id: {hex(id(self))!r} size: {self.__sizeof__()!r}]"
        )

    def __setitem__(self, key, value):
        self.__data__[key] = value

    def __getitem__(self, key):
        return self.__data__[key]


AT_STYLE = "Style"
AT_DISPLAY = "Display"
AT_SETTING = "Setting"


def make_auto(_type, instance):
    "turn an object to an auto object"
    if _type == "Style":
        globals()["@auto[style]"] = instance
        return
    elif _type == "Display":
        globals()["@auto[display]"] = instance
        return
    elif _type == "Setting":
        globals()["@auto[setting]"] = instance
        return

    raise TypeError(f"type {_type!r} it not supported as an auto object!")


def get_style(style: Style | None):
    "get the the auto style if exists or None or the past style pram"
    if style:
        return style
    if "@auto[style]" in globals():
        return globals()["@auto[style]"]


def get_display(display: "Display|None"):
    "get the auto display if exists or None or the past display pram"
    if display:
        return display
    if "@auto[display]" in globals():
        return globals()["@auto[display]"]


def get_setting(setting: Setting | None):
    "get the auto setting if exists or None or past the setting pram"
    if setting:
        return setting
    if "@auto[setting]" in globals():
        return globals()["@auto[setting]"]


class Animation:
    "Base Object For All Animations"

    class Frame:
        def __init__(self, text: str) -> None:
            self.text: str = text

    @classmethod
    def FramesFromList(cls, frames: list[Any]) -> list["Animation.Frame"]:
        result = []
        for frame in frames:
            result.append(Animation.Frame(str(frame)))

        return result

    def __init__(self, frames: list["Animation.Frame"]) -> None:
        self.frames = frames
        self.frameI = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.frameI += 1

    def __str__(self) -> str:
        return self.frames[self.frameI % len(self.frames)].text


@dataclass
class Measurements:
    """Measurements of a text"""

    columns: int
    lines: int
    text: str

    @classmethod
    def measure(cls, text: str):
        "Measure a text, stripping ANSI escape codes"
        # Regular expression to strip ANSI escape codes
        ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

        # Strip ANSI escape codes from the text
        stripped_text = ansi_escape.sub("", text)

        # Split the stripped text into lines
        l = stripped_text.split("\n")

        # Measure the maximum number of columns and the number of lines
        max_columns = len(
            max(l, key=len, default="")
        )  # Use default='' to handle empty input
        return Measurements(max_columns, len(l), stripped_text)

    def __gt__(self, value: "Measurements") -> bool:
        return self.columns + self.lines > value.columns + value.lines

    def __lt__(self, value: "Measurements") -> bool:
        return self.columns + self.lines < value.columns + value.lines

    def __le__(self, value: "Measurements") -> bool:
        return self.columns + self.lines <= value.columns + value.lines

    def __ge__(self, value: "Measurements") -> bool:
        return self.columns + self.lines >= value.columns + value.lines

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Measurements):
            raise TypeError(
                f"cannot compare the object of type {type(value)!r} to `Measurements`"
            )
        return self.columns + self.lines == value.columns + value.lines

    def __ne__(self, value: object) -> bool:
        if not isinstance(value, Measurements):
            raise TypeError(
                f"cannot compare the object of type {type(value)!r} to `Measurements`"
            )
        return self.columns + self.lines != value.columns + value.lines


class Block:
    """A Block Of Text (a multiline text) [not recommended! use `getlines` function instead!]"""

    def __init__(self, raw: str) -> None:
        self._raw = raw  # very unsafe, but might be required later
        self.measurements = Measurements.measure(self._raw)
        self.text: list[str] = self._raw.split("\n")

    def render(self) -> Generator[str, None, None]:
        for line in self.text:
            yield line

    def __str__(self) -> str:
        return "\n".join(self.text)


def getlines(string: str, *, newline: str = "\n") -> list[str]:
    return string.split(newline)


#                    (ln   col)
type Position = tuple[int, int]


class Selection:
    def __init__(self, text: str, start: Position, end: Position):
        self.text = text
        self.start = start
        self.end = end

    def __str__(self) -> str:
        lines = self.text.splitlines()
        start_line, start_col = self.start
        end_line, end_col = self.end

        # Ensure the positions are within bounds
        if (
            start_line < 0
            or end_line < 0
            or start_line >= len(lines)
            or end_line >= len(lines)
        ):
            return ""

        if start_line == end_line:
            # Selection is within the same line
            return lines[start_line][start_col:end_col]

        # Selection spans multiple lines
        selected_text = []

        # Add the text from the start line
        selected_text.append(lines[start_line][start_col:])

        # Add the text from the lines in between
        for line in range(start_line + 1, end_line):
            selected_text.append(lines[line])

        # Add the text from the end line
        selected_text.append(lines[end_line][:end_col])

        return "\n".join(selected_text)


class Display:
    def __init__(self, inital: str = "", *, auto: bool = False):
        self.text = inital
        self._alive: bool = True
        if auto == True:
            make_auto(AT_DISPLAY, self)

    def __enter__(self):
        return self

    def __exit__(self, *args): ...

    def loop(self, hook: Callable[[], str]):
        while self._alive:
            self.update(hook())
            print(codes.CLEAR, end="")
            print(str(self), end="")

    def update(self, new: str):
        self.text = new

    def __str__(self) -> str:
        return self.text


def ParseCode(code: str):
    _code = code.encode()
    i = 0
    i += 1
    if _code[i] != 91:
        get_logger().error("ParseCode()", "invalid escape code!")
        return
    i += 1
    _prams = _code[i:].decode().split(";")
    mode = _prams[0]
    prams = _prams[1:]
    return mode, prams


def GenerateCode(mode: int, prams: list[Renderable]) -> str:
    _mode = f"\x1b[{mode}"
    _prams = ";".join(str(seg) for seg in prams)
    return f"{_mode}{_prams}"


def deleteText(text: str):
    return "\b" * len(text)


# Regular expression to strip ANSI escape codes
ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def smartborder(string, padding=1, style: Style | None = None):
    "a more complex functionalitie for creating and adding borders to text, this function allows you to make more complex borders"
    style = get_style(style)
    if style:
        horizontal = style.get("Smartborder.horizontal", ["-"] * 2)
        vertical = style.get("Smartborder.vertical", ["|"] * 2)
        corners = style.get("Smartborder.corners", ["+"] * 4)
    else:
        horizontal = ["-" * 2]
        vertical = ["|"] * 2
        corners = ["+"] * 4

    # Split the input into lines
    lines = string.splitlines()

    # Strip escape codes to calculate the visible width of each line
    stripped_lines = [ansi_escape.sub("", line) for line in lines]
    max_width = max(len(line) for line in stripped_lines)

    # Create the top border
    border_top = corners[0] + horizontal[0] * (max_width + padding * 2) + corners[1]
    border_bottom = corners[2] + horizontal[1] * (max_width + padding * 2) + corners[3]

    # Create the bordered lines
    bordered_lines = [border_top]
    for line, stripped_line in zip(lines, stripped_lines):
        # Add padding around the visible text
        visible_width = len(stripped_line)
        padding_right = max_width - visible_width
        bordered_lines.append(
            f"{vertical[0]}{' ' * padding}{line}{' ' * (padding + padding_right)}{vertical[1]}"
        )
    bordered_lines.append(border_bottom)

    # Join the lines back together
    return "\n".join(bordered_lines)


def border(string, padding=1, style: Style | None = None):
    "function to add border to a string"
    style = get_style(style)
    if style:
        horizontal = style.get("Border.horizontal", "-")
        vertical = style.get("Border.vertical", "|")
        corners = style.get("Border.corners", ["+", "+", "+", "+"])
    else:
        horizontal = "-"
        vertical = "|"
        corners = ["+", "+", "+", "+"]

    # Split the input into lines
    lines = string.splitlines()

    # Strip escape codes to calculate the visible width of each line
    stripped_lines = [ansi_escape.sub("", line) for line in lines]
    max_width = max(len(line) for line in stripped_lines)

    # Create the top border
    border_top = corners[0] + horizontal * (max_width + padding * 2) + corners[1]
    border_bottom = corners[2] + horizontal * (max_width + padding * 2) + corners[3]

    # Create the bordered lines
    bordered_lines = [border_top]
    for line, stripped_line in zip(lines, stripped_lines):
        # Add padding around the visible text
        visible_width = len(stripped_line)
        padding_right = max_width - visible_width
        bordered_lines.append(
            f"{vertical}{' ' * padding}{line}{' ' * (padding + padding_right)}{vertical}"
        )
    bordered_lines.append(border_bottom)

    # Join the lines back together
    return "\n".join(bordered_lines)


def VerticalLabel(text: str):
    return "\n".join(list(text))


class ProgressBar:
    "ProgressBar Component"

    def __init__(
        self,
        default: int = 0,
        max: int = 100,
        size: int = 10,
        style: Style | None = None,
    ) -> None:
        self.value = default
        self.max = max
        self.style = get_style(style)
        self.size = size

    def update(self, amount: int = 1):
        self.value += amount

    def reset(self):
        self.value = 0

    def __str__(self):
        result = ""
        if self.style:
            left = self.style.get("ProgressBar.left", "<")
            right = self.style.get("ProgressBar.right", ">")
            tip = self.style.get("ProgressBar.tip", "o")
            line_off = self.style.get("ProgressBar.lineOff", "-")
            line_on = self.style.get("ProgressBar.lineOn", "-")
            on_color = self.style.get("ProgressBar.color:on", fg.cyan)
            off_color = self.style.get("ProgressBar.color:off", fg.grey)
        else:
            left = "<"
            right = ">"
            tip = "o"
            line_on = "-"
            line_off = "-"
            on_color = fg.cyan
            off_color = fg.grey
        amount_filled: int = self.value * self.size // self.max
        for i in range(amount_filled):
            result += (
                (on_color + tip) if i == (amount_filled - 1) else (on_color + line_on)
            )
        result += (off_color + line_off) * (self.size - amount_filled)

        return f"{left}{result}{right}\x1b[0m"


class Spinner:
    "Spiner Component (Composition `Animation` object with an default animation)"

    def _get_default_animation(self) -> Animation:
        return Animation(
            Animation.FramesFromList(["|", "/", "─", "\\", "|", "/", "─", "\\"])
        )

    def __init__(self, animation: None | Animation = None) -> None:
        self.animation: "Animation" = animation if animation != None else self._get_default_animation  # type: ignore

    def __iter__(self):
        return self

    def __next__(self):
        next(self.animation)

    def __str__(self):
        return str(self.animation)


@deprecated("The Class `DataTable` is deprecated, use the `table` function instead")
class DataTable:
    "DataTable component"

    class Column:
        "A Column Object For DataTable.Row"

        def __init__(self, text: str) -> None:
            self.text = text

        def __str__(self):
            return self.text

    class Row:
        "A Row Object for DataTable"

        def __init__(self, *cols) -> None:
            self.cols = cols

    def __init__(self, style: Style | None = None) -> None:
        self.data: list["DataTable.Row"] = []
        self.style = get_style(style)

    def add_row(self, row: "DataTable.Row"):
        self.data.append(row)

    def __str__(self):
        result = ""

        if self.style:
            seperator = self.style.get("DataTable.seperator", "|")
            left = self.style.get("DataTable.left", "[")
            right = self.style.get("DataTable.right", "]")
        else:
            seperator = "|"
            left = "["
            right = "]"

        for row in self.data:
            items = []
            for item in row.cols:
                items.append(str(item))

            result += f"{left}{f'{seperator}'.join(items)}{right}\n"

        return result


def padding(string, top=0, bottom=0, left=0, right=0):
    "function to add paddint to a string in all directions"
    # Split the input into lines
    lines = string.splitlines()

    # Strip escape codes to calculate the visible width
    stripped_lines = [ansi_escape.sub("", line) for line in lines]
    max_width = max(len(line) for line in stripped_lines)

    # Add left and right padding to each line
    padded_lines = [
        f"{' ' * left}{line}{' ' * (right + max_width - len(stripped_line))}"
        for line, stripped_line in zip(lines, stripped_lines)
    ]

    # Add top and bottom padding
    top_padding = [" " * (max_width + left + right)] * top
    bottom_padding = [" " * (max_width + left + right)] * bottom

    # Combine everything
    final_lines = top_padding + padded_lines + bottom_padding
    return "\n".join(final_lines)


class Padding:
    "Adds Padding For strings, for better experience use `padding` function instead!"

    @classmethod
    def left(cls, text: str, amount: int = 5):
        return (" " * amount) + text

    @classmethod
    def right(cls, text: str, amount: int = 5):
        return text + (" " * amount)

    @classmethod
    def center(cls, text: str, Amount: int = 5):
        return Padding.left(Padding.right(text, amount=Amount), amount=Amount)

    @classmethod
    def up(cls, text: str, amount: int = 1):
        return ((" " * len(text) + "\n") * amount) + text

    @classmethod
    def down(cls, text: str, amount: int = 1):
        return text + ((" " * len(text) + "\n") * amount)

    @classmethod
    def middle(cls, text: str, amount: int = 1):
        return Padding.down(Padding.up(text, amount=amount), amount=amount)

    @classmethod
    def complete(cls, text: str, amount: tuple[int, int] = (5, 1)):
        return Padding.middle(Padding.center(text, Amount=amount[0]), amount=amount[1])


class SwitchText:
    "SwitchText Atomic, allow you to switch between text on render"

    def __init__(self, text_a: str, text_b: str):
        self.text_a = text_a
        self.text_b = text_b
        self.switch: Literal[0, 1] = 0

    def __str__(self):
        return self.text_a if self.switch == 0 else self.text_b

    def alternate(self):
        if self.switch == 0:
            self.switch = 1
        else:
            self.switch = 0

    def update(self, text: str):
        if self.switch == 0:
            self.text_a = text
        else:
            self.text_b = text


class Input:
    "Input Component (Gets The Input On Render!)"

    def __init__(self, prompt: str = "", style: Style | None = None):
        self.prompt = prompt
        self.style = get_style(style)

    def __str__(self):
        if self.style:
            prompt = self.style.get("Input.promptText", "")
        else:
            prompt = ""
        return input(prompt)


class Title:
    "Title Desighn"

    def __init__(self, text: str):
        self.text = f"[ {text} ]"

    def __str__(self):
        return self.text


class Bar:
    "Bar Seperates Multiple Items In One Line"

    def __init__(
        self, *cols, style: Style | None = None, active: int | None = None
    ) -> None:
        self.cols = cols
        self.active = active
        self.style = get_style(style)

    def __str__(self):
        if self.style:
            sep = self.style.get("Bar.seperator", ">")
        else:
            sep = ">"
        if self.active and len(self.cols) <= self.active:
            self.cols = list(map(str, self.cols))
            self.cols[self.active] = fx.underline(self.cols[self.active])
        return f" {sep} ".join(self.cols)


class Icon:
    "Icon Desighn, An Icon For Diffrent Names"

    def __init__(self, name: str) -> None:
        self.name = name

    def __str__(self):
        return f"</{self.name.capitalize()}>"


class Chain:
    "Chain Desighn, A Chain For A Chain Of Values"

    def __init__(self, *cols, style: Style | None = None):
        self.cols = cols
        self.style = get_style(style)

    def __str__(self):
        result = ""

        if self.style:
            left = self.style.get("Chain.left", "(")
            right = self.style.get("Chain.right", ")")
            sep = self.style.get("Chain.seperator", "-")
        else:
            left = "("
            right = ")"
            sep = "-"

        for item in self.cols:
            result += f"{left}{item}{right}{sep}"

        return result[:-1]


class PrettyLogging:
    "Pretty Logging"

    def custom(self, icon, color_func, name, detail, use_stdout: bool = False):
        text = (
            color_func(icon.upper()) + " -> " + fg.cyan(name) + ": " + fg.gray(detail)
        )
        if use_stdout == True:
            print(text)
            return
        sys.stderr.write(text + "\n")
        sys.stderr.flush()

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

    def debug(self, name, detail, use_stdout: bool = False):
        text = fg.green("DEBUG") + " -> " + fg.cyan(name) + ": " + fg.gray(detail)
        if use_stdout == True:
            print(text)
            return
        sys.stderr.write(text + "\n")
        sys.stderr.flush()


def get_logger() -> PrettyLogging:
    "if `global_logger` exsist it will just return ir, if not it will create and then remove it"
    if "global_logger" not in globals():
        globals()["global_logger"] = PrettyLogging()
        return globals()["global_logger"]
    else:
        return globals()["global_logger"]


class Pointer:
    "Four Directional Pointer Desighn"

    left: str = " "
    right: str = " "
    up: str = " "
    down: str = " "


def join_string(*objs: str):
    "joins multiple string by space"
    return " ".join(objs)


def joinlines(*lines: str):
    "join multiple lines by a newline character"
    return "\n".join(lines)


@deprecated("Select is deprecated because of its bad design and functionality")
class Select:
    "MultiChoice Menu (Composition DataTable)"

    def __init__(self, choices: list[str], style: Style | None = None) -> None:
        self.dt = DataTable(style)
        self.choices = choices
        self.style = get_style(style)
        i = 0
        for choice in choices:
            self.dt.add_row(
                DataTable.Row(DataTable.Column(str(i)), DataTable.Column(choice))
            )
            i += 1

    def __str__(self):
        print(self.dt)
        while 1:
            if self.style:
                inp = input(self.style.get("Select.promptText", "> "))
            else:
                inp = input("> ")
            try:
                result = self.choices[int(inp)]
                break
            except KeyboardInterrupt:
                get_logger().info("Select", "Canceled By The User.")
                sys.exit(-1)
            except:
                get_logger().error(
                    "SelectionError",
                    "input value is not an number or out of range. try again",
                )

        return result  # type: ignore


class Br:
    "New Line Object"

    def __str__(self) -> str:
        return "\n"


class Ruler:
    "A Ruller Object that can display a length of numbers"

    def __init__(self, lenght: int, style: Style | None = None) -> None:
        self.lenght = lenght
        self.style = get_style(style)

    def __str__(self) -> str:
        result = ""

        if self.style:
            begin = self.style.get("Ruler.begin", "|")
            end = self.style.get("Ruler.end", ">")
            line = self.style.get("Ruler.line", "-")
            number_on_top: bool = self.style.get("Ruler.NumberOnTop?", False)
        else:
            begin = "|"
            end = ">"
            line = "-"
            number_on_top = False

        # the ruler it self

        if number_on_top == False:
            result += begin + (line * (self.lenght * 3)) + end + "\n"

        # the numbers

        for i in range(self.lenght + 1):
            result += str(i) + "  "
        result += "\n"

        if number_on_top == True:
            result += begin + (line * (self.lenght * 3)) + end + "\n"

        return result


# (4) point


class Mark:
    "A Mark For Behind A Text or An Option"

    _mode: bool
    _override_mode: None | tuple[str, str] = None

    def __init__(
        self, string: str, mode: bool = False, style: Style | None = None
    ) -> None:
        self.string = string
        self.style = get_style(style)
        self.mode = mode

    @property
    def mode(self):
        return self._mode

    @mode.setter
    def mode(self, new: bool):
        self._mode = new

    def __str__(self) -> str:
        if self.style:
            mark_on = self.style.get("Mark.on", "($)")
            mark_off = self.style.get("Mark.off", "( )")
        else:
            mark_on = "($)"
            mark_off = "( )"

        if self._override_mode:
            mark_on = self._override_mode[0]
            mark_off = self._override_mode[1]

        if self.mode:
            mark = mark_on
        else:
            mark = mark_off

        return f"{mark} {self.string}"


class List:
    "A List Displayt Of multiple items"

    def __init__(
        self, items: Iterable | list | tuple, style: Style | None = None
    ) -> None:
        self.style = get_style(style)
        self.items = items

    def __str__(self) -> str:
        result = ""
        if self.style:
            mode = self.style.get("List.Marker.mode", True)
        else:
            mode = True

        i = 0
        for item in self.items:
            m = Mark(item, mode, style=self.style)
            if self.style:
                if self.style.get("List.override_index", True):
                    m._override_mode = (f"{i}.", "undefined")
            result += f"{str(m)}\n"
            i += 1

        return result


class Compersition:
    "Show Relations between two object"

    def __init__(self, a, b, style: Style | None = None) -> None:
        self.a = a
        self.b = b
        self.style = get_style(style)

    def __str__(self):
        if self.style:
            not_equal = self.style.get("Compersition.not_equal", "<>")
        else:
            not_equal = "<>"
        result = ""
        if self.a == self.b:
            result += f"({self.a} == {self.b})" + " "
        if self.a != self.b:
            result += f"({self.a} {not_equal} {self.b})" + " "
        if self.a < self.b:
            result += f"({self.a} < {self.b})" + " "
        if self.a > self.b:
            result += f"({self.a} > {self.b})" + " "
        return result[:-1]


class Crop:
    "Adds Cropping to strings"

    @classmethod
    def line(cls, string: str, amount: int = 5, offset: int = 0):
        return string[offset:amount]

    @classmethod
    def text(
        cls,
        string: str,
        measurements: Measurements | None = None,
        amount: tuple[int, int] = (3, 5),  # type: ignore
        offset: tuple[int, int] = (0, 0),
    ):
        if (
            measurements
        ):  # a lot of typing errors, but trust me, this works perfectly fine
            amount: list[int] = list(amount)  # type: ignore
            amount[0] = measurements.lines  # type: ignore
            amount[1] = measurements.columns  # type: ignore
            amount: tuple[int, int] = tuple(amount)  # type: ignore

        result = ""
        lines = string.splitlines()
        for li in range(len(string)):
            if li >= amount[0]:
                break
            if li + offset[0] >= len(lines):
                break
            result += Crop.line(lines[li + offset[0]], amount[1], offset[1]) + "\n"
            li += 1

        return result[:-1]


class Notification:
    "Notification Component"

    def __init__(
        self,
        message: str,
        severity: Literal["Error", "Info", "Warning"] | None = None,
        style: Style | None = None,
    ) -> None:
        self.message = message
        self.severity = severity
        self.style = get_style(style)

    def __str__(self):
        if self.style:
            err_bg = self.style.get("Notification.error_bg", bg.red)
            err_fg = self.style.get("Notification.error_fg", fg.black)
            info_bg = self.style.get("Notification.info_bg", bg.blue)
            info_fg = self.style.get("Notification.info_fg", fg.black)
            warn_bg = self.style.get("Notification.warn_bg", bg.yellow)
            warn_fg = self.style.get("Notification.warn_fg", fg.black)
            left = self.style.get("Notification.left", "[")
            right = self.style.get("Notification.right", "]")
            do_reset = self.style.get("Notification.reset", True)
        else:
            err_bg = bg.red
            err_fg = fg.black
            info_bg = bg.blue
            info_fg = fg.black
            warn_bg = bg.yellow
            warn_fg = fg.black
            left = "["
            right = "]"
            do_reset = True

        _bg = ""
        _fg = ""
        if self.severity != None:
            match self.severity:
                case "Error":
                    _bg = err_bg
                    _fg = err_fg
                case "Info":
                    _bg = info_bg
                    _fg = info_fg
                case "Warning":
                    _bg = warn_bg
                    _fg = warn_fg
        return f"{_bg}{_fg}{left}{self.message}{right}{'\x1b[0m' if do_reset else ''}"


def fill(text: str, desired_length: int, filler: str = " "):
    "fills the infront of the `text` with the `filler` to make the text the `desired_length`"
    if len(text) >= desired_length:
        return text
    amount = desired_length - len(text)
    return text + (filler * amount)


class Tree:
    "Tree Component"

    def __init__(self, items: list[str | list]) -> None:
        self.items = items

    def _visit_node(self, items: list[str | list], depth: int = 0):
        result = ""
        for item in items:
            if isinstance(item, str):
                result += "\n" + Padding.left(item, amount=(depth * 4))
            elif isinstance(item, list):
                result += Padding.left(self._visit_node(item, depth + 1))
        return result

    def __str__(self) -> str:
        return self._visit_node(self.items)


@deprecated(
    "you can still use LegacyCanavs, but its recommended to use `Canvas` instead."
)
class LegacyCanvas:
    "Old Canavs Component"

    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self._buffer: list[list[str]] = [
            [" " for __ in range(self.width)] for _ in range(self.height)
        ]

    def clear(self):
        self._buffer = [[" " for __ in range(self.width)] for _ in range(self.height)]

    def addstr(self, x: int, y: int, string: str):
        lines = string.split("\n")
        iy = 0
        for line in lines:
            self.addline(x, y + iy, line)
            iy += 1

    def addline(self, x: int, y: int, string: str):
        if len(string.split("\n")) > 1:
            raise ValueError(
                f"expected the string: {string!r}, would be only one line, found multiple instead!"
            )
        ix = 0
        for char in string:
            self.addpixel(x + ix, y, char)
            ix += 1

    def addpixel(self, x: int, y: int, char: str):
        if x >= self.width:
            x = x % self.width
        if x < 0:
            x = 0
        if y >= self.height:
            y = y % self.height
        self._buffer[y][x] = char

    def getpixel(self, x: int, y: int):
        if x >= self.width:
            x = x % self.width
        if x < 0:
            x = 0
        if y >= self.height:
            y = y % self.height
        return self._buffer[y][x]

    def __str__(self) -> str:
        result = ""
        for row in self._buffer:
            for col in row:
                result += LegacyCanvas.RuleOneChar(col)
            result += "\n"
        return result

    @classmethod
    def RuleOneChar(cls, string: str):
        "strip a string to only one char"
        return string[0]


class Canvas:
    def __init__(self, width: int, height: int) -> None:
        self.height = height
        self.width = width
        self.buffer = [[" " for _ in range(width)] for _ in range(height)]

    def setcol(self, char: str, x: int, y: int):
        x = x % self.width
        y = y % self.height
        self.buffer[y][x] = Crop.line(char, 1)

    def getcol(self, x: int, y: int):
        x = x % self.width
        y = y % self.height
        return self.buffer[y][x]

    def push_string(self, string: str, x: int, y: int):
        lines = Block(string)

        for added_row, line in enumerate(lines.render()):
            for added_col, col in enumerate(line):
                self.setcol(col, x + added_col, y + added_row)

    def clear(self):
        self.buffer = [[" " for _ in range(self.width)] for _ in range(self.height)]

    def __str__(self):
        result = ""
        for index, row in enumerate(self.buffer):
            for col in row:
                result += col
            if index != len(self.buffer) - 1:
                result += "\n"
        return result


class ImportanceText:
    def __init__(self, messages: str, style: Style | None = None) -> None:
        self.messages = messages
        self.style = get_style(style)

    def __str__(self) -> str:
        if self.style:
            wall_fg = self.style.get("ImportanceText.fg", fg.grey)
            wall_bg = self.style.get("ImportanceText.bg", "")
        else:
            wall_fg = fg.grey
            wall_bg = ""
        return (
            wall_fg
            + wall_bg
            + "{"
            + "\x1b[0m"
            + f" {self.messages} "
            + wall_fg
            + wall_bg
            + "}"
            + "\x1b[0m"
        )


class AnsiText:

    class Segment:
        def __init__(self, text: str, is_control: bool) -> None:
            self.text = text
            self.is_control = is_control

        def __len__(self):
            return len(self.text)

    def __init__(self, segments: list["AnsiText.Segment"]) -> None:
        self.segs = segments

    def __len__(self):
        result = 0
        for seg in self.segs:
            if seg.is_control:
                continue
            result += len(seg)
        return result

    def __str__(self):
        result = ""
        for seg in self.segs:
            result += seg.text
        return result


class FilesystemDeco:
    NormalFile = lambda filename: fg.yellow(filename)
    Directory = lambda filename: fg.blue(filename)
    Executable = lambda filename: fg.red(filename) + fg.grey("*")


class Paginator:
    def __init__(
        self,
        default_page: int = 1,
        amount_of_pages: int = 5,
        style: Style | None = None,
    ) -> None:
        self.pages: int = amount_of_pages
        self.pageN = default_page + 1
        self.style = get_style(style)

    def __str__(self):
        if self.style:
            left = self.style.get("Paginator.left", "[")
            right = self.style.get("Paginator.right", "]")
            active_page = self.style.get("Paginatio.active", "o")
            unactive_page = self.style.get("Paginator.unactive", ".")
        else:
            left = "["
            right = "]"
            active_page = "o"
            unactive_page = "."
        result = left
        for i in range(self.pages):
            if i == (self.pageN % self.pages):
                result += active_page
            else:
                result += unactive_page
        return result + right


def Compose(items: list[Renderable]) -> str:
    return "\n".join(*[str(obj) for obj in items])


class Page(Renderable):
    def __init__(self, content: str, db: dict[str, Any] | None = {}) -> None:
        if not (db):
            db = {}
        self.db: dict[str, Any] = db
        self.content = content

    def __str__(self) -> str:
        result = self.content
        for key in self.db:
            value = self.db[key]
            result = result.replace(f";{key};", value)
        return result


class Scene(Renderable):
    def __init__(self, pages: list[Page]) -> None:
        self.pages = pages
        self.current_page = 1
        self.paginator = Paginator(self.current_page, len(self.pages))

    def __str__(self) -> str:
        self.paginator.pageN = self.current_page
        print(
            (Measurements.measure(str(self.pages[self.current_page])).columns + 2) * "_"
        )
        print(str(self.pages[self.current_page]))
        print(
            (Measurements.measure(str(self.pages[self.current_page])).columns + 2) * "_"
        )
        print(Padding.center(str(self.paginator)))
        _pagen: str = input("/")
        if _pagen == "q":
            return ""
        pagen = int(_pagen)
        self.current_page = pagen
        str(self)
        return ""


def table(data: list[list[str]], style: Style | None = None) -> str:
    "nice ascii tables"
    style = get_style(style)
    if style:
        left = style.get("Table.left", "[")
        right = style.get("Table.right", "]")
    else:
        left = "["
        right = "]"

    # Calculate the maximum width for each column
    def cell(text: str, width: int) -> str:
        return f"{left} {text:<{width}} {right}"  # Left-align text within the specified width

    def row(datas: list[str], widths: list[int]) -> str:
        return "".join(cell(data, widths[i]) for i, data in enumerate(datas))

    widths = [
        max(Measurements.measure(str(item)).columns for item in column)
        for column in zip(*data)
    ]

    return "\n".join(row(datas, widths) for datas in data)


def cell(
    text: str, id: int, style: Style | None = None, setting: Setting | None = None
):
    return {
        "text": text,
        "id": id,
        "style": get_style(style),
        "setting": get_setting(setting),
    }


def render_layers(
    layers: list[str], replace_space: bool = False
) -> Generator[str, None, None]:
    """Yield the rendered layers of text, moving the cursor appropriately."""

    # Constants for ANSI escape codes
    ANSI_UP = "\x1b[A"
    ANSI_RIGHT = "\x1b[C"
    ANSI_CLEAR_LINE = "\r"
    ANSI_DOWN = "\x1b[1B"

    def count_newlines(text: str) -> int:
        """Return the number of newlines in the given text."""
        return text.count("\n")

    def restore_row(text: str) -> str:
        """Return the escape sequence to move the cursor up based on the number of newlines in the text."""
        return ANSI_UP * count_newlines(text)

    def restore_col() -> str:
        """Return the escape sequence to move the cursor to the beginning of the line."""
        return ANSI_CLEAR_LINE

    for index, layer in enumerate(layers):
        if index != 0:
            # Move the cursor up and to the beginning of the line
            yield restore_row(layers[index - 1]) + restore_col()

        # Replace spaces with cursor movement to the right if specified
        if replace_space:
            layer = layer.replace(" ", ANSI_RIGHT)

        yield layer

    # Move the cursor down after rendering all layers
    yield ANSI_DOWN + "\r"


def overlap(layers: list[str]) -> str:
    biggest = max(layers, key=Measurements.measure)
    size = Measurements.measure(biggest)
    canva = Canvas(size.columns, size.lines)
    for layer in layers:
        canva.push_string(layer, 0, 0)
    return str(canva)


def t(string: str) -> Callable:
    def __call__(**kwargs):
        return string.format(**kwargs)

    return __call__


def indent(text: str, style: Style | None = None) -> str:
    style = get_style(style)
    if style:
        indentation = style.get("indent", "    ")
    else:
        indentation = "    "
    lif = lambda line: f"{indentation}{line}"
    lines = getlines(text)
    _indented_lines = map(lif, lines)
    return "\n".join(_indented_lines)


def getlevel(level: int):
    match level:
        case 1:
            return "\u2581"
        case 2:
            return "\u2582"
        case 3:
            return "\u2583"
        case 4:
            return "\u2584"
        case 5:
            return "\u2585"
        case 6:
            return "\u2586"
        case 7:
            return "\u2587"
        case 8:
            return "\u2588"
    return " "


def prettify(string: str, setting: Setting | None = None) -> str:
    """
    Prettifies the input string by replacing certain characters with their Unicode equivalents,
    collapsing spaces, replacing newlines with spaces, and converting text enclosed in double
    asterisks to uppercase.

    Args:
        string (str): The input string to be prettified.

    Returns:
        str: The prettified string.
    """
    setting = get_setting(setting)
    if setting:
        unicodeModule = setting.get("prettifier.unicode_module", False)
        spaceCollapseModule = setting.get("prettifier.space_collapse_module", True)
        intensifierModule = setting.get("prettifier.intensifire_module", True)
        innlineElementModule = setting.get("prettifier.inline_element_module", False)
    else:
        unicodeModule = False
        spaceCollapseModule = True
        intensifierModule = True
        innlineElementModule = False

    if unicodeModule:
        # Unicode characterization
        d = {
            "{": "\ufe5b",
            "}": "\ufe5c",
            "(": "\ufe59",
            ")": "\ufe5a",
            "[": "\ufe5d",
            "]": "\ufe4e",
        }

        # Replace characters using str.translate for better performance
        translation_table = str.maketrans(d)
        string = string.translate(translation_table)

    if spaceCollapseModule:
        # Collapsing spaces
        string = re.sub(r"\s+", " ", string).strip()
        string = string.replace("\n", " ")

    if intensifierModule:
        # Intensifier
        string = re.sub(r"\*\*(.*?)\*\*", lambda match: match.group(1).upper(), string)

    if innlineElementModule:
        # Inline Elements

        def elementFinder(match):
            word = match.group(1)
            match word:
                case "newline":
                    return "\n"
                case "bel":
                    return "\u0007"
                case "backspace":
                    return "\u0008"
                case "del":
                    return "\u007f"
                case "cr":
                    return "\u000d"
                case "lf":
                    return "\u000a"
            return "@" + word

        string = re.sub(r"@(\w+)", elementFinder, string)

    return string


class StrNode:
    def __init__(
        self,
        innerText: str,
        id: str | None = None,
        attributes: dict | None = None,
        setting: Setting | None = None,
    ):
        self.innerText = innerText
        self.setting = get_setting(setting)
        self.id = id
        self.attributes = attributes or {}

    def __str__(self) -> str:
        if self.setting:
            processor = self.setting.get("StrNode.processor", lambda string: string)
        else:
            processor = lambda string: string
        return processor(str(self.innerText))


class StrGroup:
    def __inti__(
        self,
        nodes: list["StrNode|StrGroup"],
        id: str | None = None,
        attributes: dict | None = None,
    ):
        self.nodes = nodes
        self.id = id
        self.attributes = attributes or {}

    def query(self, id: str):
        results = []
        for node in self.nodes:
            if node.id == id:
                results.append(node)
        return results

    def __str__(self) -> str:
        return "".join(map(str, self.nodes))


###############Ported From `CuteUi.py`###################


class Statusline(Renderable):
    def __init__(self, data: list[Renderable], style: Style | None = None):
        self.style = get_style(style)
        self.data: list[str] = list(map(str, data))

    def __str__(self) -> str:
        if self.style:
            left = self.style.get("Statusline.left", "<")
            right = self.style.get("Statusline.right", ">")
            seperator = self.style.get("Statusline.seperator", ".")
        else:
            left = "<"
            right = ">"
            seperator = "."

        return left + seperator.join(self.data) + right


class Clock(Renderable):
    def __init__(self, style: Style | None = None) -> None:
        self.style = get_style(style)

    @property
    def time(self) -> dict[str, Renderable]:
        from datetime import datetime

        now = datetime.now()
        date: dict[str, Renderable] = {
            "hour": str(now.hour),
            "minute": str(now.minute),
            "second": str(now.second),
        }

        return date

    def __str__(self) -> str:
        if self.style:
            template = self.style.get("Clock.template", "hour:minute:second")
            left = self.style.get("Clock.left", "(")
            right = self.style.get("Clock.right", ")")
        else:
            template = "hour:minute:second"
            left = "("
            right = ")"
        _rendered_time: str = template
        for key, value in self.time.items():
            _rendered_time = _rendered_time.replace(key, str(value))
        result = f"{left}{_rendered_time}{right}"
        return result


class HighlightedLabel(Renderable):
    def __init__(self, text: str, style: Style | None = None) -> None:
        self.text = Block(text)
        self.style = get_style(style)

    def __str__(self) -> str:
        if self.style:
            tabs = self.style.get("HighlightedLabel.tabs", 1)
            marker = self.style.get("HighlightedLabel.marker", "|")
        else:
            tabs = 1
            marker = "|"

        result = ""
        for line in self.text.render():
            result += f"{marker}{'\t'*tabs}{line}{Br()}"
        return result


def TyperAnimation(text: str, *, end: str = "\n") -> Animation:
    frames: list[Renderable] = []

    string = ""
    for char in text + end:
        string += char
        frames.append(string + "_")

    return Animation(Animation.FramesFromList(frames))


def BlinkAnimation(text: str, length: int, *, end: str = "\n") -> Animation:
    frames: list[Renderable] = []
    for i in range(length):
        if i % 2 == 0:
            frames.append(("#" * len(text) + end))
        else:
            frames.append(("_" * len(text) + end))
    frames.append(text + end)
    return Animation(Animation.FramesFromList(frames))


class _SelectorNetwork(dict[str, object]): ...


globals()["@auto[_SelectorNetwork]"] = _SelectorNetwork()


def useId[T](obj: T, *, Id: str) -> T:
    setattr(obj, "_selector_id", Id)
    network: _SelectorNetwork = globals()["@auto[_SelectorNetwork]"]
    network[Id] = obj
    return obj


class Selector[T]:
    def __init__(self, Id: str) -> None:
        self._selector_Id = Id

    @property
    def object(self) -> T | None:
        obj = globals()["@auto[_SelectorNetwork]"].get(self._selector_Id, None)
        if hasattr(obj, "_selector_id"):
            if getattr(obj, "_selector_id") == self._selector_Id:
                return obj
        return None

    @classmethod
    def query(cls, Id: str):
        return Selector(Id)


class Meter(Renderable):
    _value: int

    def __init__(
        self, initial: int, start: int, end: int, style: Style | None = None
    ) -> None:
        assert end > start, "Meter: End Value Should Be Bigger Than The Start Value"
        assert (initial < end) or (
            initial > start
        ), "initial value should be between the start-end value"
        assert start >= 0, "start value should be above zero"
        self.start = start
        self.end = end + 1
        self.value = initial
        self.initial = initial
        self.style = get_style(style)

    def increase(self, amount: int = 0):
        self.value += amount

    def decrease(self, amount: int = 0):
        self.value -= amount

    def reset(self):
        self.value = self.initial

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new: int):
        self._value = new

    def _compile_meter_display(self) -> str:
        result = ""
        if self.style:
            seperator = self.style.get("Meter.seperator", " ")
        else:
            seperator = " "
        for i in range(self.start, self.end - self.start):
            result += f"{i}{seperator}"
        return result[:-1]

    def _compile_pointer(self, pointer_char: str) -> str:
        result = ""
        for i in range(self.start, self.end - self.start):
            if i == self.value:
                result += f"{pointer_char} "
            else:
                result += "  "
        return result[:-1]

    def __str__(self) -> str:
        if self.style:
            mode: Literal["horizontal", "vertical"] = self.style.get(
                "Meter.mode", "horizontal"
            )  # mode should be 'horizontal' or 'vertical'
            assert mode not in [
                "horizontal",
                "vertical",
            ], "Meter: style mode should be 'horizontal' or 'vertical'."
            pointer = self.style.get("Meter.pointer", "^")
        else:
            mode = "horizontal"
            pointer = "^"

        result = ""

        result += self._compile_meter_display()
        result += "\n"
        result += self._compile_pointer(pointer)

        return result


def linenumber(text: str, style: Style | None = None, *, data: str = "") -> str:
    processed = Block(text)
    style = get_style(style)
    if style:
        seperator = style.get("linenumber.seperator", "  | ")
    else:
        seperator = f"  | "
    result = ""
    for ln, line in enumerate(processed.render()):
        result += f"{ln}{seperator}{data}{line}\n"
    return result


class Table:
    def __init__(self, headers: list[str] | None = None, style: Style | None = None):
        self.headers = headers if headers else []
        self.headers = list(
            map(lambda string: Padding.center(string, Amount=2), self.headers)
        )
        self.rows: list[list[Renderable]] = []
        self.style = get_style(style)

    def add_row(self, row: list[Renderable]):
        if len(row) != len(self.headers):
            raise ValueError("Row length must match header length.")
        self.rows.append(row)

    def add_column(self, header: str, column_data: list[Renderable]):
        if len(column_data) != len(self.rows):
            raise ValueError("Column data length must match number of rows.")
        self.headers.append(header)
        for i, data in enumerate(column_data):
            self.rows[i].append(data)

    def _fix_size(self):
        for index, row in enumerate(self.rows):
            for index2, cell in enumerate(row):
                amount = len(self.headers[index2])
                row[index2] = Crop.line(fill(str(cell), amount), amount=amount)

    def __str__(self) -> str:
        if self.style:
            separator = self.style.get("Table.separator", " | ")
        else:
            separator = " | "

        # make headers
        header_row = separator.join(self.headers)
        rendered_table = f"{header_row}\n"
        rendered_table += "-" * len(header_row) + "\n"
        self._fix_size()

        # make rows
        for row in self.rows:
            rendered_row = separator.join(map(str, row))
            rendered_table += f"{rendered_row}\n"

        return rendered_table


def highlight(text: str, selection: Selection, style: Style | None = None):
    style = get_style(style)
    if style:
        code = style.get("Highlight.code", "\x1b[7m")
    else:
        code = "\x1b[7m"

    processed = Block(text)
    start = selection.start
    end = selection.end

    end_line = processed.text[end[0]]
    end_line = list(end_line)  # type: ignore
    end_line.insert(end[1], "\x1b[0m")  # type: ignore
    processed.text[end[0]] = "".join(end_line)

    start_line = processed.text[start[0]]
    start_line = list(start_line)  # type: ignore
    start_line.insert(start[1], code)  # type: ignore
    processed.text[start[0]] = "".join(start_line)

    return str(processed)


class Summery:
    def __init__(self, text: str, detail: str, style: Style | None = None) -> None:
        self.text = text
        self.detail = Block(detail)
        self._flag = 0b0
        self.style = get_style(style)

    def toggle(self):
        if self._flag == 0b0:
            self._flag = 0b1
        else:
            self._flag = 0b0

    def __str__(self) -> str:
        if self.style:
            marker = self.style.get("Summery.marker", "*")
        else:
            marker = "*"
        result = ""
        result += f"{marker if self._flag == 0b1 else " "} {self.text}: \n"
        if self._flag == 0b1:
            for line in self.detail.render():
                result += Padding.left(f"{line}\n", amount=4)
        return result


def note(text: str, message: str, ln: int):
    processed = Block(text)
    result = ""
    for cln, line in enumerate(processed.render()):
        if ln == cln:
            result += f"{line} {message}\n"
            continue
        result += line + "\n"
    return result


###########################################################
