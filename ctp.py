"content text processor"
from contextlib import contextmanager
from io import StringIO
from typing import Callable, Optional
from threading import Lock

_global_document: StringIO = StringIO()
"the global wireless document object"

_global_render_lock: bool = True
"wether the renderer is in write mode or render mode"

_global_render_processors: list[Callable[[StringIO], StringIO]] = []
"the global list of processors that run on every document changes"

_document_lock = Lock()
"protects _global_document and _global_render_lock"

_processors_lock = Lock()
"protects _global_render_processors"


@contextmanager
def console():
    "the raw console to make changes to the document"
    global _global_document
    with _document_lock:
        doc = StringIO(_global_document.read())
    yield doc
    doc.seek(0)
    with _document_lock:
        if _global_render_lock == True:
            for proc in _global_render_processors:
                doc = proc(doc)
            _global_document = doc
        else:
            _global_document.seek(0)


def set_processor(processor: Callable[[StringIO], StringIO]) -> None:
    "add a new processor"
    global _global_render_processors
    with _processors_lock:
        _global_render_processors.append(processor)


def render(file: Optional[str] = None) -> str:
    "render the buffer (optionally into a file as well)"
    with _document_lock:
        content = "" if (_global_render_lock == True) else _global_document.read()

    if file:
        with open(file, "w") as _f:
            _f.write(content)
    return content


def close() -> None:
    "close the global render lock and lock any further changes, preparing for render"
    global _global_render_lock

    with _document_lock:
        _global_render_lock = False


def echo(*string: str) -> None:
    "echo the content into the buffer"
    with console() as con:
        con.write("".join(string))


def clear() -> None:
    "clear the entire buffer"
    with console() as con:
        con.seek(0)
        con.truncate()


def load(content: str) -> None:
    "clears thw whole buffer and replcae it with new content"
    clear()
    echo(content)
