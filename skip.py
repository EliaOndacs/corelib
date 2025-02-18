"implements the skip virtual machine interface and a class to run it"

from typing import Any


type NodeData = tuple
"a type that holds the data passed into the node visitor function"
type Node = tuple[str, NodeData]
"a type that stores the node type and its `NodeData`"


class SkipVM:
    "Skip Virtual Machine (Notice: This Class Does NOT Implement Any Sort Of Behavior And Its Only Made To Be Inherited)"

    def __init__(self, default_scope: dict[str, Any] | None = None) -> None:
        self.scope: dict[str, Any] = default_scope or {}

    def visit(self, node: Node):
        "visit a node and return its result"

        def default(*_):
            print(
                f"skip_vm(warning): no visit method defined for the node type {node[0]!r}"
            )
            return None

        return getattr(self, f"visit_{node[0]}", default)(*node[1])

    def run(self, program: list[Node]):
        "run and visit a list of nodes and return a list of result returned from visiting each node"
        result = []
        for node in program:
            result.append(self.visit(node))
        return result


def mknode(_type: str, *data) -> Node:
    "generate a new node (may be more convenient)"
    return (_type, data)
