"""
corelib module that makes it 10000000000000000000000000x percent easier
to make filesystem structures,

here's an example:
```python
from makefs import mkfs

mkfs({
    "name": "test_dir",
    "items": [
        {
            "name": "test.py",
            "text": "print('hello, world!')\"
        },
        {
            "name": "conent_dir",
            "items": [
                {
                    "name": "info.txt",
                    "text": "password: *******\n"
                }
            ]
        }
    ]
})

```

this will make a filesystem tree that looks like this:

[test_dir]
    - test.py

    [content_dir]
        - info.txt

"""

import os
from typing import TypedDict


class _FileBlueprint(TypedDict):
    name: str
    text: str


class _DirectoryBlueprint(TypedDict):
    name: str
    items: list["_DirectoryBlueprint|_FileBlueprint"]


def file(map: _FileBlueprint, parent: str | None = None):
    fullpath = map["name"]
    if parent:
        fullpath = os.path.join(parent, map["name"])
    with open(fullpath, "w") as _FH:
        _FH.write(map["text"])
        _FH.close()


def mkfs(map: _DirectoryBlueprint, parent: str | None = None):
    fullpath = map["name"]
    if parent:
        fullpath = os.path.join(parent, map["name"])
    if not os.path.exists(fullpath):
        os.mkdir(fullpath)
    for item in map["items"]:
        if item.get("text", None):
            file(item, parent=fullpath)  # type: ignore
            continue
        mkfs(item, parent=fullpath)  # type: ignore

