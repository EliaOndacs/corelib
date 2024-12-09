import os
from io import TextIOWrapper
from enum import Enum, auto
from pathlib import Path


class SocketType(Enum):
    ST_IO = auto()


class Session:
    def __init__(self, socket_type: SocketType, port: int):
        self.port = port
        self.__id__ = (self.port + (0 if socket_type == SocketType.ST_IO else 1)) ** 10
        self.socket_type = socket_type

    @property
    def SessionId(self) -> int:
        """returns the SessionID"""
        return self.__id__

    def exit(self):
        os.remove(os.path.expanduser(_get_path(self)))

def _get_path(session):
    return f"~/_{session.SessionId}"


class SocketIOError(OSError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SocketIO:
    def __init__(self, session: Session):
        self.session = session
        self.fd: list[None | TextIOWrapper] = [None, None]

    def _reload_content(self):
        self.fd[0] = Path(_get_path(self.session)).expanduser().absolute().open("r")

    def open(self):
        if not(Path(_get_path(self.session)).expanduser().absolute().exists()):
            self.fd[1] = Path(_get_path(self.session)).expanduser().absolute().open("w")
            if self.fd[1]:
                self.fd[1].write("")
        else:
            self.fd[1] = Path(_get_path(self.session)).expanduser().absolute().open("r+")
        self._reload_content()
        

    def read(self) -> str:
        if self.fd[0]:
            self._reload_content()
            return self.fd[0].read()
        else:
            raise SocketIOError("Null FileDescriptor, Cannot Read!")

    def write(self, data: str):
        if self.fd[1]:
            self.fd[1].write(data)
        else:
            raise SocketIOError("Null FileDescriptor, Cannot Write!")

    def close(self):
        if self.fd[0]:
            self.fd[0].close()
        if self.fd[1]:
            self.fd[1].close()
        self.fd = [None, None]

class Socket:
    def __init__(self, session: Session) -> None:
        self.session = session
        if session.socket_type == SocketType.ST_IO:
            self.mode = "io"

        self.socket: SocketIO 

        if self.mode == "io":
            self.socket = SocketIO(self.session)

        self.setup()

    def setup(self):
        self.open = self.socket.open
        self.read = self.socket.read
        self.write = self.socket.write
        self.close = self.socket.close

    def __enter__(self):
        self.socket.open()
        return self.socket

    def __exit__(self, *_):
        self.socket.close()
        return
