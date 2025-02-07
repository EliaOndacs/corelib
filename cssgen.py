"""
cssgen makes it this much easier to create cascate style sheet
"""

from typing import Any


def _mkbody(childs):
    return "\n".join(childs)


def rule(selector, *childs) -> str:
    return selector + " {" + _mkbody(childs) + "}\n"


def dictrule(selector, body: dict[str, Any]) -> str:
    childs = []
    for _proprety in body:
        value = body[_proprety]
        childs.append(declarate(_proprety, value))
    return rule(selector, *childs)


def stylesheet(*rules) -> str:
    return _mkbody(rules)


def declarate(name: str, value: str) -> str:
    return f"  {name}: {value};"
