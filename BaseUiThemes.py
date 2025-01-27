from typing import Any
from ansi.colour import fg


# simulate [copy and paste] BaseUi `Style` object
class Style:
    def __init__(self, options: dict[str, Any]):
        self.__data__: dict[str, Any] = options
        self.get = self.__data__.get

    def __repr__(self):
        return f"[object of 'Style' id: {hex(id(self))!r} size: {self.__sizeof__()!r}]"

    def __setitem__(self, key, value):
        self.__data__[key] = value

    def __getitem__(self, key):
        return self.__data__[key]


smooth_cute = Style(
    {
        "Border.horizontal": "─",
        "Border.vertical": "│",
        "Border.corners": ["┌", "┐", "└", "┘"],
        "ProgressBar.left": "[",
        "ProgressBar.right": "]",
        "ProgressBar.tip": ">",
        "ProgressBar.lineOff": " ",
        "ProgressBar.lineOn": "=",
        "ProgressBar.color:on": fg.yellow,
        "DataTable.seperator": "│",
        "DataTable.right": "│",
        "DataTable.left": "│",
        "Bar.seperator": ":",
        "Chain.left": "{",
        "Chain.right": "}",
        "Chain.seperator": "~",
        "Ruler.begin": "/",
        "Ruler.end": ">",
        "Ruler.line": "-",
        "List.override_index": True,
        "Compersition.not_equal": "!=",
        "Notification.left": "(",
        "Notification.right": ")",
    }
)


minimal_space = Style(
    {
        "Border.horizontal": " ",
        "Border.vertical": "│",
        "Border.corners": ["┌", "┐", "└", "┘"],
        "ProgressBar.left": " ",
        "ProgressBar.right": " ",
        "ProgressBar.tip": ">",
        "ProgressBar.lineOn": "-",
        "ProgressBar.lineOff": " ",
        "ProgressBar.color:on": fg.grey,
        "DataTable.seperator": " : ",
        "DataTable.left": " ",
        "DataTable.right": " ",
        "Table.left": "",
        "Table.right": "",
        "Bar.seperator": "%",
        "Chain.left": " ",
        "Chain.right": " ",
        "Chain.seperator": "-",
        "Select.promptText": ":",
        "Ruler.begin": " ",
        "Ruler.end": ">",
        "Ruler.line": "-",
        "Mark.off": " ",
        "Mark.on": "*",
        "Compersition.not_equal": "!=",
        "Notification.left": "|",
        "Notification.right": "|",
        "ImportanceText.fg": fg.red,
        "Paginator.left": " ",
        "Paginator.right": " ",
        "Input.promptText": ": ",
    }
)
