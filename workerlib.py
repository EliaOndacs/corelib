from threading import Thread
from types import CodeType
from typing import Any, Optional
import uuid


class Worker:
    code: CodeType
    scope: dict[str, Any]
    _id: str

    def __init__(self, code: str, *, scope: Optional[dict[str, Any]] = None) -> None:
        self._id = f"Wroker.{uuid.uuid4()}"
        self.code = compile(code, self._id, "exec")
        self.scope = scope or {}

    def spawn(self):
        t = Thread(target=self)
        t.start()
        return t

    def __call__(self):
        exec(
            self.code,
            globals=self.scope,
            locals={k: v for k, v in self.scope.items() if k.startswith("DEFINE_")},
        )

    def get_id(self):
        return self._id


