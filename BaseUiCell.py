from dataclasses import dataclass
from typing import Callable


class Crop:  # from BaseUi (copy and paste!)
    @classmethod
    def line(cls, string: str, amount: int = 5, offset: int = 0):
        return string[offset:amount]

    @classmethod
    def text(
        cls,
        string: str,
        amount: tuple[int, int] = (3, 5),
        offset: tuple[int, int] = (0, 0),
    ):
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


@dataclass
class Cell:
    name: str
    function: Callable[[str], str]
    width: int
    height: int
    scroll: tuple[int, int] = (0, 0)

    def __str__(self) -> str:
        rawstr: str = self.function(self.name)
        result: str = Crop.text(
            rawstr, amount=(self.height, self.width), offset=self.scroll
        )
        return result
