from copy import copy, deepcopy
from typing import Any, Literal

type ContextStatus = Literal[0, 1, 2]
"""
if
0: working.
1: completed.
2: error!
"""


class context[T]:
    _value: T | None
    _status: ContextStatus
    _gt: dict[str, Any]

    def __init__(self, initial: T|None = None) -> None:
        self._gt = {}
        self.status: ContextStatus = 0
        self.value: T | None = initial

    @property
    def status(self) -> ContextStatus: # type: ignore
        """
        current status of the Context

        NOTE: use `context.done` instead to check if the context
        """
        return self._status

    @status.setter
    def status(self, new: ContextStatus): # type: ignore
        self._status = new

    @property
    def done(self):
        """
        if the context is completed or not

        NOTE: if theres an error this will still return True

        Returns:
            bool: True if the context is complete, False if not
        """
        if self.status == 0:
            return False
        return True

    @property
    def value(self) -> T | None: # type: ignore
        "Single Value Restored By The Context"
        return self._value

    @value.setter
    def value(self, new: T): # type: ignore
        self._value = new

    def snapshot(self, use_deepcopy: bool = False):
        """\
        takes a snapshot of the global var table (`globals()`) and copy it into its own global var table

        Args:
            use_deepcopy (bool, optional): use `deepcopy()` instead of `copy()` from the built-in `copy` module. Defaults to False.
        Raises:
            TypeError (Only On Usage Of deepcopy): if it fails to make a copy of an object

        """
        if use_deepcopy == True:
            copy_func = deepcopy
        else:
            copy_func = copy
        self._gt = copy_func(globals())

    def __getitem__(self, key) -> Any:
        return self._gt.get(key, "undefined")

    def __setitem__(self, key, value) -> None:
        self._gt[key] = value
        return

    def cancel(self):
        "cancel the context without an error"
        self.status = 1

    def error(self):
        "cancel the context with an error"
        self.status = 2

    def __repr__(self) -> str:
        return "<class 'context'>"
