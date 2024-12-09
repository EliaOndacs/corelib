from typing import overload


class UnsupportedOperation(NotImplementedError): ...


class StreamBase:
    def __init__(self, value: str = "") -> None:
        self._raw_data: str = value
        self.position = 0

    def insert(self, value: str):
        raise UnsupportedOperation(
            "function Stream.insert is not supported on this StreamType!"
        )

    def append(self, value: str):
        raise UnsupportedOperation(
            "function Stream.append is not supported on this StreamType!"
        )

    def fetch(self):
        raise UnsupportedOperation(
            "function Stream.fetch is not supported on this StreamType!"
        )

    def mov(self, offset: int = 1):
        raise UnsupportedOperation(
            "function Stream.mov is not supported on this StreamType!"
        )

    def on_update(self, event: tuple[str, list[str|int|None]]): ...

    def __str__(self) -> str:
        return self._raw_data

    def __repr__(self):
        return f"<Stream data: {str(self)!r}>"


class PureStream(StreamBase):
    def __init__(self, value: str = "") -> None:
        self._raw_data: str = value
        self.position = 0

    def insert(self, value: str, *, _local=False):
        old = self._raw_data
        self._raw_data = (
            self._raw_data[: self.position]
            + value
            + self._raw_data[self.position + 1 :]
        )
        if _local!=True:
            self.on_update(("insert", [old, self._raw_data, value]))

    def append(self, value: str):
        old = self._raw_data
        _old_pos = self.position
        self.position = len(self._raw_data) + 1
        self.insert(value,_local=True)
        self.on_update(("append",[old, self._raw_data, value, _old_pos]))

    def fetch(self):
        self.on_update(("fetch", [None]))
        return self._raw_data[self.position-1 :]

    def mov(self, offset: int = 1):
        old = self.position
        self.position += offset
        self.on_update(("mov", [old, self.position, offset]))

    def __str__(self) -> str:
        return self._raw_data

    def __repr__(self):
        return f"<Stream data: {str(self)!r}>"




