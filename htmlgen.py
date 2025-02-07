"""
generate html code within python, making it this much easier
"""

from typing import Any
from dataclasses import dataclass, field


def _unfilter_attributes(attrs: dict[str, Any]) -> dict[str, Any]:
    new: dict[str, Any] = {}
    for key in attrs:
        orig = key
        if key == "classname":
            key = "class"
        new[key.replace("_", "-")] = attrs[orig]
    return new


def _generate_attributes(attrs: dict[str, Any]) -> str:
    result = ""
    attrs = _unfilter_attributes(attrs)
    for key in attrs:
        if key in [
            "controls",
            "loop",
            "muted",
            "checked",
            "disabled",
            "readonly",
            "required",
            "autofocus",
            "multiple",
            "novalidate",
            "defer"
        ]:
            result += f" {key}"
        else:
            result += f' {key}="{attrs[key]}"'
    return result


def _mkbody(childs):
    return "".join(childs)


@dataclass
class Element:
    name: str
    text: str
    attrs: dict[str, Any] = field(default_factory=dict)
    is_selfclosing: bool = False

    def __str__(self) -> str:
        result = "<"
        result += self.name
        result += _generate_attributes(self.attrs)
        if self.is_selfclosing == True:
            result += "/>"
        else:
            result += ">"
            result += self.text
            result += "</"
            result += self.name
            result += ">"
        return result


def useAutoRefresh(time: int = 1) -> str:
    return f'<meta http-equiv="refresh" content="{str(time)}">'


def doctype(_type: str = "html"):
    return f"<!DOCTYPE {_type}>"


def span(text: str, **kwds):
    return str(Element("span", text, kwds))


def p(text: str, **kwds):
    return str(Element("p", text, kwds))


def h1(text: str, **kwds):
    return str(Element("h1", text, kwds))


def h2(text: str, **kwds):
    return str(Element("h2", text, kwds))


def h3(text: str, **kwds):
    return str(Element("h3", text, kwds))


def h4(text: str, **kwds):
    return str(Element("h4", text, kwds))


def h5(text: str, **kwds):
    return str(Element("h5", text, kwds))


def h6(text: str, **kwds):
    return str(Element("h6", text, kwds))


def div(*childs, **kwds):
    return str(Element("div", "".join(childs), kwds))


def script(text: str, **kwds):
    return str(Element("script", text, kwds))


def head(*childs, **kwds):
    return str(Element("head", _mkbody(childs), kwds))


def body(*childs, **kwds):
    return str(Element("body", _mkbody(childs), kwds))


def meta(**kwds):
    return str(Element("meta", "", kwds))


def title(text: str):
    return str(Element("title", text, {}))


def a(text: str, ref: str):
    return str(Element("a", text, {"href": ref}))


def img(*childs, ref: str, **kwds):
    return str(Element("img", _mkbody(childs), {"src": ref, **kwds}))


def audio(*childs, ref: str, **kwds):
    return str(Element("audio", _mkbody(childs), {"src": ref, **kwds}))


def video(*childs, **kwds):
    return str(Element("video", _mkbody(childs), kwds))


def source(*childs, **kwds):
    return str(Element("source", _mkbody(childs), kwds))


def br():
    return str(Element("br", "", {}))


def button(text: str, **kwds):
    return str(Element("button", text, kwds))


def hr():
    return str(Element("hr", "", {}))


def style(text: str, **kwds):
    return str(Element("style", text, kwds))


def ul(*childs, **kwds):
    return str(Element("ul", _mkbody(childs), kwds))


def li(text: str, **kwds):
    return str(Element("li", text, kwds))


def ol(*childs, **kwds):
    return str(Element("ol", _mkbody(childs), kwds))


def iframe(*childs, src: str, **kwds):
    return str(Element("iframe", _mkbody(childs), {"src": src, **kwds}))


def mainelement(*childs, **kwds):
    return str(Element("main", _mkbody(childs), kwds))


def htmlelement(*childs, **kwds):
    return str(Element("html", _mkbody(childs), kwds))


def article(*childs, **kwds):
    return str(Element("article", _mkbody(childs), kwds))


def table(*childs, **kwds):
    return str(Element("table", _mkbody(childs), kwds))


def tr(*childs, **kwds):
    return str(Element("tr", _mkbody(childs), kwds))


def th(text: str, **kwds):
    return str(Element("th", text, kwds))


def td(text: str, **kwds):
    return str(Element("td", text, kwds))


def summary(*childs, **kwds):
    return str(Element("summary", _mkbody(childs), kwds))


def details(*childs, **kwds):
    return str(Element("details", _mkbody(childs), kwds))


def textarea(text, **kwds):
    return str(Element("textarea", text, kwds))


def label(text: str, **kwds):
    return str(Element("label", text, kwds))


def inputelement(text: str, **kwds):
    return str(Element("input", text, kwds))


def select(*childs, **kwds):
    return str(Element("select", _mkbody(childs), kwds))


def form(*childs, **kwds):
    return str(Element("form", _mkbody(childs), kwds))


def option(text: str, **kwds):
    return str(Element("option", text, kwds))


def progress(text: str, **kwds):
    return str(Element("progress", text, kwds))


def ruby(text: str, **kwds):
    return str(Element("ruby", text, kwds))


def nav(*childs, **kwds):
    return str(Element("nav", _mkbody(childs), kwds))


def dialog(*childs, **kwds):
    return str(Element("dialog", _mkbody(childs), kwds))


def canvas(text: str, **kwds):
    return str(Element("canvas", text, kwds))


def header(*childs, **kwds):
    return str(Element("header", _mkbody(childs), kwds))


def footer(*childs, **kwds):
    return str(Element("footer", _mkbody(childs), kwds))


def element(name: str, *childs, **kwds):
    return str(Element(name, _mkbody(childs), kwds))
