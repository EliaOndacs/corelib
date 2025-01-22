from app import Application
from elements import *
from helpers import *


@component
def UserProfile(username: str, isPaid: bool):
    return f"[ {username} <{'+' if isPaid else ' '}> ]"  # [ User123 < > ]


@application
def main(app: Application):
    return div(
        UserProfile("EliaOndacs", app.storage["isPaid"]),
        rule(),
        br(),
        "hello, world!",
        br(),
    )
