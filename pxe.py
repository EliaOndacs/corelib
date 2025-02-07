"""
build and load python files into a custom format called 'pxe'
"""

from dataclasses import dataclass
from types import ModuleType
import marshal, pickle


@dataclass
class PxeFileHeader:
    name: str
    version: str
    length: int
    directExecutable: bool


def BuildPxe(
    code: str, name: str, version: str, directExecutable: bool = False
) -> tuple[bytes, bytes]:
    _code_type = compile(code, name, "exec", optimize=2)
    length = _code_type.__sizeof__()
    header = PxeFileHeader(name, version, length, directExecutable)
    return marshal.dumps(_code_type), pickle.dumps(header)


def RunPxe(data: bytes, header: bytes):
    _header = pickle.loads(header)
    _code_type = marshal.loads(data)
    if _header.directExecutable == False:
        raise EnvironmentError(
            f"pxe: {_header.name!r} cannot be loaded as a executable, because its a library."
        )
    module = ModuleType(_header.name)
    exec(_code_type, module.__dict__)
    return


def LoadPxe(data: bytes, header: bytes):
    _header = pickle.loads(header)
    _code_type = marshal.loads(data)
    if _header.directExecutable == True:
        raise EnvironmentError(
            f"pxe: {_header.name!r} cannot be loaded as a library, because its a direct executable."
        )
    module = ModuleType(_header.name)
    exec(_code_type, module.__dict__)
    return module
