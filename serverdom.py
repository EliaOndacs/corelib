from dataclasses import dataclass, field
from typing import Any, cast
import urllib
import urllib.parse


@dataclass
class Location:
    href: str
    protocol: str = ""
    host: str = ""
    hostname: str = ""
    port: int | None = None
    pathname: str = ""
    search: str = ""
    query: dict | None = None
    hash: str = ""

    def __post_init__(self):
        parsed_url = urllib.parse.urlparse(self.href)
        self.protocol = parsed_url.scheme
        self.host = parsed_url.netloc
        self.hostname = cast(str, parsed_url.hostname)
        self.port = parsed_url.port
        self.pathname = parsed_url.path
        self.search = parsed_url.query
        self.hash = parsed_url.fragment
        self.query = urllib.parse.parse_qs(parsed_url.query)


@dataclass
class DocumentNode:
    text: str
    nodeName: str
    id: str | None = None
    classname: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    childs: list["DocumentNode"] = field(default_factory=list)
    segments: list["DocumentNode|str"] = field(default_factory=list)
    title: str = ""
    parentNode: "DocumentNode|None" = None
    visibilityState: bool = True

    def clear(self):
        self.childs = []
        self.segments = []

    def getRootNode(self) -> "Document|DocumentNode":
        if self.parentNode == None:
            return self
        return self.parentNode.getRootNode()

    def getElementById(self, _id: str):
        for child in self.childs:
            if child.id == _id:
                return child
            if elm := child.getElementById(_id):
                return elm
        return None

    def getElementByTagName(self, name: str):
        for child in self.childs:
            if child.nodeName == name:
                return child
            if elm := child.getElementByTagName(name):
                return elm
        return None

    def getElementByClassName(self, classname: str):
        for child in self.childs:
            if child.classname == classname:
                return child
            if elm := child.getElementByClassName(classname):
                return elm
        return None

    def append(self, node: "DocumentNode"):
        self.childs.append(node)
        self.segments.append(node)
        node.parentNode = self

    def remove(self, node: "DocumentNode"):
        self.childs.remove(node)
        self.segments.remove(node)
        node.parentNode = None

    def write(self, string: str):
        self.segments += string

    def writeln(self, string: str, *, end="\n\r"):
        self.segments += string + end

    def render(self, indent: int = 0) -> str:
        if not self.visibilityState:
            return ""
        result = self.text
        for segment in self.segments:
            if isinstance(segment, DocumentNode):
                result += segment.render(indent + 1)
            else:
                result += str(segment)
        return result

    def __str__(self) -> str:
        return self.render()

    def __repr__(self) -> str:
        return f'<{self.nodeName} id="{self.id}">{self.text}...</{self.nodeName}>'


class Document(DocumentNode): ...


document = Document("", "@root")
