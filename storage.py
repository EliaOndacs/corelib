import contextlib
import pickle
import os
from pathlib import Path
import sys
from typing import Any, TypedDict


class ApplicationClass(TypedDict):
    name: str
    platform: str


def AppConfig(app_class: ApplicationClass):
    """allows you to have config directory for your application"""

    _config_path = Path(f"~/.config/{app_class['name']}").expanduser()
    if not _config_path.exists():
        _config_path.mkdir()
    return _config_path


class EnvironmentStorage:
    """allows you to set environment variables and files"""

    def __init__(self, app_class: ApplicationClass) -> None:
        self.app_class = app_class

    def create_file(self, path: str, data: str):
        self[path] = {"path": path, "data": data}

    def get_file(self, path: str):
        file = self[path]
        assert not (file), f"file {path!r} not found!"
        return file["data"]  # type: ignore

    def __setitem__(self, key, value):
        os.environ[key] = value

    def __getitem__(self, key):
        return os.environ.get(key, None)


def CacheStorage(app_class: ApplicationClass) -> Path:
    """returns the path the application cache directory"""
    match app_class["platform"]:
        case "win32":
            first = Path("C:/ProgramData/").expanduser()
            second = first / app_class["name"]
            second.mkdir(exist_ok=True)
            return second

        case "darwin":
            first = Path("/Library/Caches").expanduser()
            second = first / app_class["name"]
            second.mkdir(exist_ok=True)
            return second

        case "linux":
            first = Path("/var/cache").expanduser()
            second = first / app_class["name"]
            second.mkdir(exist_ok=True)
            return second

    raise OSError(f"un-supported operating system")


class RuntimeStorage:
    def __init__(self, app_class) -> None:
        self.app_class = app_class
        self.runtime_storage_path = RuntimeStorage.get_runtime_path(app_class)
        self._runtime_storage: dict[str, Any] = {}

    @classmethod
    def get_runtime_path(cls, Class: ApplicationClass):
        match Class["platform"]:

            case "win32":
                first = Path("~/AppData/Local").expanduser()
                second = first / Class["name"]
                second.mkdir(exist_ok=True)
                return second

            case "linux":
                first = Path("~/.local/share").expanduser()
                second = first / Class["name"]
                second.mkdir(exist_ok=True)
                return second

            case "darwin":
                first = Path("~/Library/Application Support").expanduser()
                second = first / Class["name"]
                second.mkdir(exist_ok=True)
                return second

        raise OSError(f"un-supported operating system")

    def open(self, filename: str, mode: str = "r"):
        return (self.runtime_storage_path / filename).open(mode=mode)

    def set(self, variable: str, value: Any):
        self._runtime_storage[variable] = value

    def get(self, variable: str):
        return self._runtime_storage.get(variable, None)

    def save(self):
        with self.open("data", "wb") as output:
            pickle.dump(self._runtime_storage, output)

    def load(self):
        with self.open("data", "rb") as _input:
            self._runtime_storage = pickle.load(_input)


@contextlib.contextmanager
def storage(name: str):
    _class: ApplicationClass = {"name": name, "platform": sys.platform}
    st = RuntimeStorage(_class)
    try:
        yield st
    finally:
        st.save()
