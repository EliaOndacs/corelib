"""
fabric - symbolic tree nodes for building DSLs, ASTs, and UI/HTML trees.

provides:
- group: container node with children
- symbol: leaf node with data
- group(name)/symbol(name): helpers to create nodes
- walk(node): depth-first tree traversal
- transform(node, fn): bottom-up tree transformer that applies `fn` with evaluated children


example:
```python
from corelib.fabric import group, symbol, walk, transform

div = group("div")
span = symbol("span")
text = symbol("text")

tree = div(span(text("Hello")), span(text("World")))

# walk through the tree
for node in walk(tree):
    print(node)

# transform the tree into HTML
def render(node, values):
    if node.name == "div": return "<div>" + "".join(values) + "</div>"
    if node.name == "span": return "<span>" + "".join(values) + "</span>"
    if node.name == "text": return "".join(values)
    return "".join(values)

print(transform(tree, render))
```
output:
```html
<div><span>Hello</span><span>World</span></div>
```

"""

from typing import Any, Callable, Generator
from dataclasses import dataclass, field
from contextlib import contextmanager
from functools import wraps


@dataclass
class Group:
    "a base group class used to store a group of children that can be other `Group` objects or `Symbol` objects"

    name: str
    children: list["Group|Symbol|object"] = field(default_factory=list)

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

    def constructor(*nodes: Group | Symbol | object) -> Group:
        return Group(name, list(nodes))

    return constructor


def symbol(name: str) -> Callable[..., Symbol]:
    "a utility helper function used to create constructors for symbol types"

    def constructor[T](*data: Any | T) -> Symbol[Any | T]:
        return Symbol(name, list(data))

    return constructor


def walk(node: Group | Symbol | object):
    "allows you walk through all the nodes in a tree"
    if isinstance(node, Group) or isinstance(node, Symbol):
        yield node
    if isinstance(node, Group):
        for child in node.children:
            yield from walk(child)
    elif isinstance(node, Symbol):
        for child in node.data:
            if isinstance(child, (Group, Symbol)):
                yield from walk(child)


def transform(
    node: Group | Symbol | object,
    fn: Callable[[Group | Symbol | object, list[Any]], Any],
) -> Any:
    "recursively applies `fn` bottom-up, evaluating children first and passing their results to the parent"
    if isinstance(node, Group):
        children_values = [transform(child, fn) for child in node.children]
        return fn(node, children_values)
    elif isinstance(node, Symbol):
        data_values = [
            transform(d, fn) if isinstance(d, (Group, Symbol)) else d for d in node.data
        ]
        return fn(node, data_values)
    else:
        return node


def from_transformer(fn: Callable[[Group | Symbol | object, list[Any]], Any]):
    "a decorator to turn any function into a transformer"

    @wraps(fn)
    def wrapper(node: Group | Symbol | object):
        return transform(node, fn)

    return wrapper


@contextmanager
def push[T](stack: list[T], item: T) -> Generator[T, None, None]:
    stack.append(item)
    yield stack.pop()
