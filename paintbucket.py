from typing import Callable, Protocol
import ansi, re

__all__ = [
    "text",
    "push",
    "clear",
    "newline",
    "register",
    "Screen",
    "set_alt_screen",
    "frame",
    "div",
    "border",
    "padding",
    "goto",
    "Renderable",
    "Color",
]

_string = ""
type Color = tuple[int, int, int]


class Renderable(Protocol):
    def __str__(self) -> str: ...


# Regular expression to strip ANSI escape codes
ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

def indent(string, amount=0):
    lines = string.splitlines()
    final = map((lambda line: ((' '*amount)+line)), lines)
    return "\n".join(final)

def padding(string, top=0, bottom=0, left=0, right=0):
    "function to add paddint to a string"
    # Split the input into lines
    lines = string.splitlines()

    # Strip escape codes to calculate the visible width
    stripped_lines = [ansi_escape.sub('', line) for line in lines]
    max_width = max(len(line) for line in stripped_lines)

    # Add left and right padding to each line
    padded_lines = [
        f"{' ' * left}{line}{' ' * (right + max_width - len(stripped_line))}"
        for line, stripped_line in zip(lines, stripped_lines)
    ]

    # Add top and bottom padding
    top_padding = [' ' * (max_width + left + right)] * top
    bottom_padding = [' ' * (max_width + left + right)] * bottom

    # Combine everything
    final_lines = top_padding + padded_lines + bottom_padding
    return '\n'.join(final_lines)

def border(string, padding=1):
    "function to add border to a string"
    # Split the input into lines
    lines = string.splitlines()

    # Strip escape codes to calculate the visible width of each line
    stripped_lines = [ansi_escape.sub("", line) for line in lines]
    max_width = max(len(line) for line in stripped_lines)

    # Create the top border
    border = "+" + "-" * (max_width + padding * 2) + "+"

    # Create the bordered lines
    bordered_lines = [border]
    for line, stripped_line in zip(lines, stripped_lines):
        # Add padding around the visible text
        visible_width = len(stripped_line)
        padding_right = max_width - visible_width
        bordered_lines.append(
            f"|{' ' * padding}{line}{' ' * (padding + padding_right)}|"
        )
    bordered_lines.append(border)

    # Join the lines back together
    return "\n".join(bordered_lines)


class Screen:
    @classmethod
    def render(cls):
        "render the made text"
        print(_string, end="")

    @classmethod
    def push_text(cls, text: str):
        "low level api, should not use, use `push` instead"
        global _string
        _string += text

    @classmethod
    def clear(cls):
        "clear the made text. if mid render, use `clear` instead"
        global _string
        _string = ""

class div:
    "a class to make divs in the ui"
    _string: str = ""

    def __str__(self) -> str:
        return self._string

    def push_text(self, text: str):
        self._string += str(text)


def _get_handle(screen: div | None):
    "low level api, not for direct use!"
    if screen:
        return screen.push_text
    else:
        return None


def push(text: Renderable, *, handler: Callable[[str], None] | None = None):
    "paint text. its better to use the `text` instead."
    if not (handler):
        Screen.push_text(str(text))
    else:
        handler(str(text))


def text(
    string: str,
    *,
    background: Color | None = None,
    color: Color | None = None,
    end: str = "\x1b[0m\n",
    screen: div | None = None,
):
    "displays a text with options"
    if not (background):
        bg = ""
    else:
        bg = ansi.color.rgb.rgb256(*background, bg=True)
    if not (color):
        fg = ""
    else:
        fg = ansi.color.rgb.rgb256(*color)
    _s = fg + bg + string + end

    push(_s, handler=_get_handle(screen))


def clear(*, screen: div | None = None):
    "clears the screen"
    push("\x1b[H\x1b[2J", handler=_get_handle(screen))


def set_alt_screen(value: bool = True, *, screen: div | None = None):
    "set the terminal alternative screen on and off"
    if not (value):
        push("\033[?1049l", handler=_get_handle(screen))
    else:
        push("\033[?1049h", handler=_get_handle(screen))
        clear(screen=screen)


def register(*, screen: div | None = None):
    "low lever api function for registering commands, use `newline` instead."
    push("\r", handler=_get_handle(screen))


def newline(*, screen: div | None = None):
    "add newline"
    register(screen=screen)
    push("\n", handler=_get_handle(screen))


def goto(x: int, y: int, *, screen: div | None = None):
    "moves the cursor to x, y"
    push(ansi.cursor.goto(y, x), handler=_get_handle(screen))
    register(screen=screen)


def frame(text: Renderable, *, screen: div | None = None):
    "function to add a bordered text"
    push(border(str(text)), handler=_get_handle(screen))
    newline(screen=screen)


