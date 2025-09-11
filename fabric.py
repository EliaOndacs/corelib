"""
fabric - symbolic tree nodes for building DSLs, ASTs, and UI/HTML trees.

provides:
- group: container node with children
- symbol: leaf node with data
- group(name)/symbol(name): helpers to create nodes
- walk(node): depth-first tree traversal

example:
```python
from corelib.fabric import group, symbol, walk

div = group("div")
span = symbol("span")

tree = div(span("Hello"), span("World"))
for node in walk(tree):
    print(node)
```
"""

from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Group:
    "a base group class used to store a group of children that can be other `Group` objects or `Symbol` objects"

    name: str
    children: list["Group|Symbol"] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Group):
            return False
        if self.name != other.name:
            return False
        if self.children != other.children:
            return False
        return True

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.children)))


@dataclass
class Symbol[T]:
    "a base symbol class used to store and create symbol with a name and data"

    name: str
    data: list[T] = field(default_factory=list)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Symbol):
            return False
        if self.name != other.name:
            return False
        if self.data != other.data:
            return False
        return True

    def __hash__(self) -> int:
        return hash((self.name, tuple(self.data)))


def group(name: str) -> Callable[..., Group]:
    "a utility helper function used to create constructors for group types"

    def constructor(*nodes: Group | Symbol) -> Group:
        return Group(name, list(nodes))

    return constructor


def symbol(name: str) -> Callable[..., Symbol]:
    "a utility helper function used to create constructors for symbol types"

    def constructor[T](*data: Any | T) -> Symbol[Any | T]:
        return Symbol(name, list(data))

    return constructor


def walk(node: Group | Symbol):
    "allows you walk through all the nodes in a tree"
    yield node
    if isinstance(node, Group):
        for child in node.children:
            yield from walk(child)
    elif isinstance(node, Symbol):
        for child in node.data:
            if isinstance(child, (Group, Symbol)):
                yield from walk(child)
