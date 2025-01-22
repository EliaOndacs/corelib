from app import Application
from component import Component

__all__ = ["component", "application"]


def component(func):
    return Component(func, func.__name__)


def application(func):
    main: Component[Application] = component(func)
    app = Application(main)

    app.run()
