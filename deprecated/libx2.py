from typing import Literal


class I:
    """
    Position(x: int, y: int) -> tuple[int, int]
    """

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __setitem__(self, name: Literal["x", "y"], value: int = 0):
        match name:
            case "x":
                self.x = value
            case "y":
                self.y = value

    def __getitem__(self, name: Literal["x", "y"]):
        match name:
            case "x":
                return self.x
            case "y":
                return self.y

    def __index__(self):
        return self.x, self.y


Position = I
Index = I
