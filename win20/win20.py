from enum import Enum, auto
from BaseUi import *  # pack: ignore
from BaseUiVdom import *  # pack: ignore
from dataclasses import dataclass


class TextLayer:
    def compose(self) -> Generator[str | Any, None, None]:
        yield from ()

    def __str__(self) -> str:
        result = list(self.compose())
        final_result = map((lambda item: str(item)), result)
        return "".join(final_result)


class AnsiLayer:
    def compose(self) -> Generator[str, None, None]:
        yield from ()

    def __str__(self) -> str:
        final_result = list(self.compose())
        return "".join(final_result)


class IconLayer:
    def compose(self) -> Generator[str, None, None]:
        yield from ()

    def __str__(self) -> str:
        final_result = list(self.compose())
        return "".join(final_result)


type MediaLayer = TextLayer | AnsiLayer


class WinType(Enum):
    Normal = auto()
    Float = auto()
    Notification = auto()
    Segement = auto()


@dataclass()
class WinClass:
    width: int
    height: int
    Type: WinType = WinType.Normal


class Window:
    def __init__(self, Class: WinClass) -> None:
        self._winclass = Class
        self.canvas = Canvas(self._winclass.width, self._winclass.height)
        self.dom = DOM()

    def replaceLayer(self, id: str, replaceMedia: MediaLayer, **attributes):
        for node in self.dom.query(id):
            node.replaceWith(replaceMedia)
            node.setAttribute(attributes)

    def append(self, media: MediaLayer, id: str = "$None", **attributes):
        self.dom.insertNode(DOMNode(str(media), id, **attributes))

    def update(self):
        self.canvas.addstr(0, 0, str(self.dom))

    def clear(self):
        del self.canvas
        self.canvas = Canvas(self._winclass.width, self._winclass.height)

    def __str__(self):
        return str(self.canvas)
