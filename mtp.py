from typing import Any, Callable
from bs4 import BeautifulSoup, Tag


class TextReplacer:
    """
    A class used to replace placeholders in a text with actual values.

    Attributes:
    ----------
    model : dict[str, Any]
        A dictionary containing the placeholders and their corresponding values.

    Methods:
    -------
    __setitem__(key, value)
        Sets a new placeholder and its value in the model.
    __call__(text: str)
        Replaces the placeholders in the text with their actual values.
    """

    def __init__(self, model: dict[str, Any]) -> None:
        self.model = model

    def __setitem__(self, key, value):
        self.model[key] = value

    def __call__(self, text: str):

        for key in self.model:
            text = text.replace(f"<-{key}->", str(self.model[key]))

        return text


def Condition(text: str):
    """
    A function used to evaluate conditional statements in a text.

    Parameters:
    ----------
    text : str
        The text containing the conditional statements.

    Returns:
    -------
    str
        The text with the conditional statements evaluated.
    """

    mk = BeautifulSoup(text, "html.parser")
    nodes: list[Tag] = mk.find_all("if")
    for node in nodes:
        if "a" not in node.attrs:
            raise ValueError(f"expected an attribute 'a' in node {node!r}")
        a = node.attrs["a"]
        if "b" not in node.attrs:
            raise ValueError(f"expected an attribute 'b' in node {node!r}")
        b = node.attrs["b"]
        if a == b:
            node.replace_with(node.text)
        else:
            node.decompose()
    return str(mk)


def Repetition(text: str):
    """
    A function used to repeat a text a specified number of times.

    Parameters:
    ----------
    text : str
        The text to be repeated.

    Returns:
    -------
    str
        The repeated text.
    """

    mk = BeautifulSoup(text, "html.parser")
    nodes: list[Tag] = mk.find_all("rep")
    for node in nodes:
        if "amount" not in node.attrs:
            raise ValueError(f"expected an attribute 'amount' in node {node!r}")
        amount = int(node.attrs["amount"])
        node.replace_with(f'{(node.text+"\n")*amount}')
    return str(mk)


def CreateElements(text: str, name: str, elements: list[dict[str, Any]]):
    """
    A function used to create elements in a text based on a template.

    Parameters:
    ----------
    text : str
        The text containing the template.
    elements : list[dict[str, Any]]
        A list of dictionaries containing the data to be used in the template.

    Returns:
    -------
    str
        The text with the elements created.
    """

    mk = BeautifulSoup(text, "html.parser")
    node = mk.find(name)
    if node is None:
        raise SyntaxError(f"could't find the '{name.upper()}' tag in the html")

    result = ""
    for element in elements:
        result += TextReplacer(element)(node.text)
        result += "\n"
    node.replace_with(result)
    return str(mk)


def useTagFunction(text, funcs: dict[str, Callable]):
    """
    A function used to apply functions to tags in a text.

    Parameters:
    ----------
    text : str
        The text containing the tags.
    funcs : dict[str, Callable]
        A dictionary containing the functions to be applied to the tags.

    Returns:
    -------
    str
        The text with the functions applied to the tags.
    """

    mk = BeautifulSoup(text, "html.parser")
    nodes: list[Tag] = mk.find_all()
    for tag in nodes:
        if tag.name in funcs:
            tag.replace_with(funcs[tag.name](tag.name, tag.text, tag.attrs))
    return str(mk)


def callFunctions(text: str, funcs: dict[str, Callable]):
    """
    A function used to call functions in a text.

    Parameters:
    ----------
    text : str
        The text containing the function calls.
    funcs : dict[str, Callable]
        A dictionary containing the functions to be called.

    Returns:
    -------
    str
        The text with the functions called.
    """

    for name in funcs:
        text = text.replace(f"{name}()", funcs[name]())
    return text
