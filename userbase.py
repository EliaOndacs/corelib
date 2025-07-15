from uuid import UUID, uuid4
from dataclasses import dataclass, field
from typing import Any, Callable


class RequestDenied(Exception): ...


@dataclass
class User:
    username: str
    group: "UserGroup|None" = None
    attrs: dict[str, Any] = field(default_factory=dict)
    uid: UUID = uuid4()

    @property
    def displayName(self):
        return self.username.replace(" ", "").capitalize()

    def __repr__(self) -> str:
        return f"@{self.displayName}"

    def join(self, group: "UserGroup"):
        if group.request(self):
            self.group = group
        else:
            raise RequestDenied(
                f"{self.displayName}: request denied to join the group {group.displayName}"
            )


@dataclass
class UserGroup:
    groupname: str
    request_handler: Callable[["UserGroup", User], bool]
    users: list[User] = field(default_factory=list)

    @property
    def displayName(self):
        return f"({self.groupname.replace(" ", "").capitalize()})"

    def request(self, user: User) -> bool:
        return self.request_handler(self, user)

    def __repr__(self) -> str:
        result = self.displayName + "\n"
        result += "\n".join(map((lambda x: "   - " + repr(x)), self.users))
        return result
