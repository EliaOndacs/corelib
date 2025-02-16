from dataclasses import dataclass, field
from typing import SupportsIndex, Any


class NodeNotFoundError(Exception): ...


@dataclass
class Domnode:
    "a domnode object"
    _object: object
    _id: str
    childs: list["Domnode"] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def query(self, _id: str):
        if _id == self._id:
            return self
        for child in self.childs:
            if child._id == _id:
                return child

    def push(self, node: "Domnode"):
        self.childs.append(node)

    def insert(self, index: SupportsIndex | int, node: "Domnode"):
        self.childs.insert(index, node)


@dataclass
class Dom:
    "a global implementation for a document object model (dom)"
    nodes: list[Domnode] = field(default_factory=list)

    def push(self, node: Domnode):
        self.nodes.append(node)

    def insert(self, index: SupportsIndex | int, node: Domnode):
        self.nodes.insert(index, node)

    def query(self, selector: str):
        for node in self.nodes:
            if return_node := node.query(selector):
                return return_node
        raise NodeNotFoundError(
            f"node with the selector [ id: {selector!r} ] not found!"
        )
