from pathlib import Path
from helpers import component
from utils import getTerminalWidth
import requests  # type: ignore

__all__ = ["br", "div", "span", "p", "script", "file", "link", "rule"]


@component
def br():
    return "\n"


@component
def div(*childs):
    return "".join(childs)


@component
def p(text: str):
    return text


@component
def span(text: str):
    return text


@component
def script(code: str):
    return eval(code)


@component
def file(path: str):
    P = Path(path).expanduser()
    assert P.exists(), f"file {path!r} not found!"
    return P.read_text()


@component
def link(url: str, json=None) -> str:
    return requests.get(url, json=json).text


@component
def rule(*, char: str = "-"):
    return div(br(), char * getTerminalWidth(), br())
