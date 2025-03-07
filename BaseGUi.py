from contextlib import contextmanager
import tkinter, os
from tkinter import Menu, ttk
from typing import Callable, Literal
from functools import wraps


windows: list[tkinter.Tk|tkinter.Frame|ttk.Frame] = []
widgets: list[tuple[int, tkinter.Widget]] = []
_class: dict = {}

_auto: int = -1


def auto():
    global _auto
    _auto += 1
    return _auto


@contextmanager
def frame():
    global windows 
    frame = tkinter.Frame(getwin())
    windows.append(frame)
    frame.configure(**_class)
    widgets.append((auto(), frame))
    yield frame
    windows.pop()


@contextmanager
def window():
    global windows
    screen = tkinter.Tk()
    windows.append(screen)
    screen.configure(**_class)
    yield screen
    screen.mainloop()
    windows.pop()


def packFrame(frame: ttk.Frame):
    frame.pack()


def getwin():
    global windows
    return windows[-1]


def query(selector: int):
    for widget in widgets:
        if widget[0] == selector:
            yield widget[1]


def query_one(selector: int):
    results = list(query(selector))
    assert len(results) <= 1
    if len(results) == 0:
        return
    return results[0]


def widget(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global widgets
        _id = auto()
        w = func(*args, **kwargs)
        w.configure(**_class)
        widgets.append((_id, w))
        return w

    return wrapper


def winclass(**kwargs):
    global _class
    _class = kwargs


@widget
def text(text: str):
    return tkinter.Label(getwin(), text=text)


@widget
def button(text: str, callback: Callable):
    return tkinter.Button(getwin(), text=text, command=callback)


@widget
def textbox(text: str):
    return tkinter.Message(getwin(), text=text)


@widget
def canvas():
    return tkinter.Canvas(getwin())


@widget
def listview(
    name: str, mode: Literal["single", "browse", "multiple", "extended"] = "extended"
):
    return tkinter.Listbox(getwin(), selectmode=mode, name=name)


@widget
def progressbar(initial: float = 0):
    return ttk.Progressbar(getwin(), value=initial)


@widget
def rulebar():
    return ttk.Separator(getwin())


@widget
def scale(name: str, *, to: float = 100):
    return tkinter.Scale(getwin(), name=name, to=to)


@widget
def checkbutton(text: str, callback: Callable):
    return ttk.Checkbutton(getwin(), text=text, command=callback)


@widget
def radiobutton(text: str, callback: Callable):
    return ttk.Radiobutton(getwin(), text=text, command=callback)


@widget
def notebook(name: str):
    return ttk.Notebook(getwin(), name=name)


@widget
def menubutton(menu: tkinter.Menu, text: str):
    return ttk.Menubutton(getwin(), menu=menu, text=text)


def menu(
    title: str,
    type: Literal["menubar", "tearoff", "normal"] = "normal",
    *,
    parent: None | tkinter.Menu = None
):
    return tkinter.Menu(parent or getwin(), title=title, type=type)


@widget
def optionmenu(callback: Callable, *values):
    return ttk.OptionMenu(getwin(), command=callback, *values)


def packall(**options):
    global widgets
    for widget in widgets:
        widget[1].pack(**options)


def setmenu(menu: tkinter.Menu):
    getwin().config(menu=menu)

def settitle(title: str):
    getwin().title(title)

def seticon(path: str):
    # Get the file extension
    _, ext = os.path.splitext(path)
    
    # Check the extension and set the icon accordingly
    if ext.lower() == '.ico':
        getwin().iconbitmap(path)  # Use iconbitmap for .ico files
    elif ext.lower() == '.gif':
        # Use iconphoto for .gif files
        icon_photo = tkinter.PhotoImage(file=path)
        getwin().iconphoto(False, icon_photo)
    else:
        raise Exception("Unsupported icon file type. Please use `.ico` or `.gif`.")

def update_class(w):
    w.configure(**_class)


def create_menu(parent, menu_dict):
    for label, action in menu_dict.items():
        if isinstance(action, dict):  # If the action is a dictionary, create a submenu
            submenu = tkinter.Menu(parent, tearoff=0, **_class)
            submenu.configure(**_class)
            create_menu(submenu, action)  # Recursively create the submenu
            parent.add_cascade(label=label, menu=submenu, **_class)
        else:  # Otherwise, it's a command
            parent.add_command(
                label=label, command=action, **_class
            )  # Use globals to get the function


@contextmanager
def menubar():
    m = menu("root")
    yield m
    setmenu(m)


def application(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        with window() as win:
            return_value = func(win, *args, **kwargs)
        return return_value

    return wrapper

def msgbox(title: str, message: str, *, severity: Literal["info", "error", "warning"] = "info"):
    import tkinter.messagebox as tk_msgbox
    match severity:
        case "info":
            tk_msgbox.showinfo(title, message)
        case "error":
            tk_msgbox.showerror(title, message)
        case "warning":
            tk_msgbox.showwarning(title, message)

@widget
def textarea():
    return tkinter.Text(getwin())

@widget
def textfield():
    return tkinter.Entry(getwin())
