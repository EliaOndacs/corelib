"""
a corelib framework that combines other packages
from corelib to give you a full client side framework
to build cli/tui apps or combine with sanic for web development
"""

from .pipex import *
from .phelix import *
from .makefs import *
from sqllex import types, SQLite3x  # type: ignore
from pydantic import BaseModel
from .eventquery import *
from .datatype import *
from .util import *
from .workerlib import Worker
from .rod import r
from .detacls import deta
from . import stream
from .serverdom import *
from .userbase import *
from .storage import storage
import click
from pathlib import Path
from .maskslib import *

VERSION = "0.1.0"
