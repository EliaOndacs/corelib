try:
    from BaseUi import *  # pack: ignore
except ModuleNotFoundError:
    from system.corelib.BaseUi import * # pack: ignore

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
        assert start > 0, "start value should be above zero"
        self.start = start
        self.end = end + 2
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
        code = style.get("highlight.code", "\x1B[7m")
    else:
        code = "\x1B[7m"

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

