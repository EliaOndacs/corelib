"""
a library for rgb colors in ansi
"""

from ansi.colour.rgb import rgb256

def __getattr__(attr: str):
    if attr.startswith("fg_"):
        hex_color = attr[3:]
        values = hex_color.split("_")
        assert len(values) == 3
        r, g, b = int(values[0]), int(values[1]), int(values[2])
        return rgb256(r, g, b)
    elif attr.startswith("bg_"):
        hex_color = attr[3:]
        values = hex_color.split("_")
        assert len(values) == 3
        r, g, b = int(values[0]), int(values[1]), int(values[2])
        return rgb256(r, g, b, True)
    elif attr == "reset":
        return "\x1b[0m"
    else:
        return globals()[attr]
