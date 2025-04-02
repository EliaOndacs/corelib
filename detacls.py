from dataclasses import dataclass, field
from typing import Any, Callable, Self, final

type Modifire[T] = Callable[[T], Any]
type Checker[T] = Callable[[T], bool] | type


@final
@dataclass
class deta[T]:
    value: T
    doc: str = "[NO INFORMATION PROVIDED]"
    _meta: list = field(default_factory=list)

    def describe(self, message: str) -> Self:
        """
        change the __doc__ attribute of the object and the deta instance,
        it will be mentioned as metadata in the json conversion
        """
        self.doc = message
        return self

    def isTypeof(self, expected: type) -> Self:
        "raises an error if the value is not of the expected type"
        assert isinstance(
            self.value, expected
        ), f"expected the value of {self.value!r} to be a type of {expected!r}"
        return self

    def meta(self, *content):
        "add mtadata to the object before calling the `repr` function on each object passed through"
        self._meta.extend(map(repr, content))

    def json(self) -> dict[str, Any]:
        "returns a python dictionary that can be turned into json or any other format"
        data: dict[str, Any] = (
            vars(self.value) if hasattr(self.value, "__dict__") else {}
        )
        data["@metadata"] = self._meta
        data["@value"] = self.value
        data["@doc"] = self.doc
        return data

    def modify(self, *modifires: Modifire[T]) -> Self:
        "modify the object using the passed modifires"
        for modifire in modifires:
            self.value = modifire(self.value)
        return self

    def check(self, *checkers: Checker[T]) -> Self:
        "use to checkers to make sure the data is validated. otherwise will throw an type error"
        for checker in checkers:
            if isinstance(checker, type):
                self.isTypeof(checker)
                continue
            assert checker(
                self.value
            ), f"check failed with the data {self.value!r} on the checker {checker!r}"
        return self

