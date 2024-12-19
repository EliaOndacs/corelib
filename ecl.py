from shlex import shlex
from dataclasses import dataclass
from typing import Any

@dataclass
class Flag:
    name: str

    def __repr__(self) -> str:
        return f"Flag('-{self.name}')"

@dataclass
class Data[T]:
    value: T

    def __repr__(self) -> str:
        return str(self.value)

class String(Data[str]):
    ...
class Integer(Data[int]):
    ...
class Boolean(Data[bool]):
    ...
class Word(Data[str]):
    ...

@dataclass
class Command:
    name: str

type action = tuple[Command, list[String | Integer | Boolean | Flag | Word ]]

def parse_line(line: str) -> action|None:
    parser = shlex(line, punctuation_chars=True)
    tokens: list = []
    name = parser.get_token()
    if not (name):
        return None
    tokens.append(Command(name))
    arguments: list[String | Integer | Boolean | Flag | Word ] = []
    for arg in parser:
        if arg[0] == "-":
            arguments.append(Flag(arg[1:]))
            continue
        if arg.isdigit():
            arguments.append(Integer(int(arg)))
            continue
        if arg == "true":
            arguments.append(Boolean(True))
            continue
        if arg == "false":
            arguments.append(Boolean(False))
            continue
        if arg[0] == '"':
            string = arg[1:-1]
            arguments.append(String(string))
            continue
        arguments.append(Word(arg))
    tokens.append(arguments)
    return tokens[0], tokens[1]


def parse(text: str) -> list[action]:
    result: list[action] = []
    for line in text.splitlines():
        cmd = parse_line(line)
        if cmd:
            result.append(cmd)
    return result


def execute_line(action, scope: dict[str, Any]):

    command = action[0]
    prams = action[1]

    match command.name:
        case "set":
            if not(isinstance(prams[0], Word)):
                print(f"|    error: expected an variable name!\n|    got {type(prams[0]).__name__!r} instead!")
                exit()
            scope[prams[0].value] = prams[1]

        case "print":
            if isinstance(prams[0], Word):
                print(scope.get(prams[0].value, "undefined"))
            else:
                print(prams[0].value)

        case _:
            if command.name in scope:
                scope = scope[command.name](scope, *prams)
    return scope

def execute(ast: list[action], scope: dict[str, Any]|None):
    scope = scope or {}
    for line in ast:
        scope = execute_line(line, scope) # type: ignore 
    return scope

def program(text: str, *, default_scope: dict[str, Any]|None = None):
    ast = parse(text)
    result = execute(ast, default_scope)
    return result
