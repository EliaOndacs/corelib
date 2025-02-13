"""
build and load python files into a custom format called 'pxe'
"""

from dataclasses import dataclass
from types import ModuleType
import marshal, pickle

__all__ = [
    "PXE_VERSION",
    "PxeFileHeader",
    "BuildPxe",
    "RunPxe",
    "LoadHeader",
    "LoadPxe",
]
PXE_VERSION = 1


@dataclass
class PxeFileHeader:
    name: str
    version: str
    length: int
    directExecutable: bool
    pxe_version: int = PXE_VERSION


def BuildPxe(
    code: str,
    name: str,
    version: str,
    directExecutable: bool = False,
    pxeVersion: int = PXE_VERSION,
) -> tuple[bytes, bytes]:
    "generates a pxe format based on a python code and header data"
    _code_type = compile(code, name, "exec", optimize=2)
    length = _code_type.__sizeof__()
    header = PxeFileHeader(name, version, length, directExecutable, pxeVersion)
    return marshal.dumps(_code_type), pickle.dumps(header)


def RunPxe(data: bytes, header: bytes):
    "runs a pxe format as an executable, cannot be a library"
    _header: PxeFileHeader = pickle.loads(header)
    if PXE_VERSION < _header.pxe_version:
        raise EnvironmentError(
            f"pxe: pxe version (pxe {_header.pxe_version}) not supported by this copy!"
        )
    _code_type = marshal.loads(data)
    if _header.directExecutable == False:
        raise EnvironmentError(
            f"pxe: {_header.name!r} cannot be loaded as a executable, because its a library."
        )
    module = ModuleType(_header.name)
    exec(_code_type, module.__dict__)
    return


def LoadHeader(header: bytes) -> PxeFileHeader:
    "loads just the pxe header data"
    return pickle.loads(header)


def LoadPxe(data: bytes, header: bytes):
    "load a pxe format as an library, cannot be a direct executable"
    _header = pickle.loads(header)
    if PXE_VERSION < _header.pxe_version:
        raise EnvironmentError(
            f"pxe: pxe version (pxe {_header.pxe_version}) not supported by this copy!"
        )
    _code_type = marshal.loads(data)
    if _header.directExecutable == True:
        raise EnvironmentError(
            f"pxe: {_header.name!r} cannot be loaded as a library, because its a direct executable."
        )
    module = ModuleType(_header.name)
    exec(_code_type, module.__dict__)
    return module
