import os


def getTerminalHeight():
    return os.get_terminal_size().lines


def getTerminalWidth():
    return os.get_terminal_size().columns
