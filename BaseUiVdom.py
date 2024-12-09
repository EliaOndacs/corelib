from typing import Any


class DOMNode:
    _component: Any
    _attrs: dict[str, Any]

    def __init__(self, component, id: str, childs: list["DOMNode"] = [], **attrs):
        self.component = component
        self.childs = childs
        self.id = id
        self.attributes = attrs

    @property
    def attributes(self):
        return self._attrs

    @attributes.setter
    def attributes(self, new):
        self._attrs = new

    def setAttribute(self, attr: dict[str, Any]):
        self._attrs = {**self._attrs, **attr}

    @property
    def component(self):
        return self._component

    @component.setter
    def component(self, new: Any):
        self._component = new

    @component.deleter
    def component(self):
        del self._component

    def __str__(self):
        return str(self.component)

    def replaceWith(self, component):
        self.component = component

    def query(self, id: str):
        result = []
        for child in self.childs:
            if child.id == id:
                result.append(child)
            result.extend(child.query(id))
        return result

    def insertNode(self, node: "DOMNode"):
        self.childs.append(node)

    def render(self):
        result = ""
        for child in self.childs:
            result += str(child)
            result += child.render()
        return result


class DOM(DOMNode):
    def __init__(self, childs: list["DOMNode"] = []):
        super().__init__('', "$DOM", childs)

    def __str__(self):
        return self.render()
