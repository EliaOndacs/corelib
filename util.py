import os
import sys


class Symbol[OptionalTyping]:
    "the Symbol class allows you to construct symbol type which is unique every time."
    data: OptionalTyping | None = None

    def __str__(self):
        return str(self.data) if self.data else "[ object of type symbol ]"


class entry:
    "function decorator for the program entry function"

    def __init__(self, function) -> None:
        try:
            code = function()
            if code:
                os._exit(code)
            os._exit(0)
        except KeyboardInterrupt:
            os._exit(-1)
        except Exception as err:
            sys.excepthook(type(err), err, err.__traceback__)
            os._exit(-1)
