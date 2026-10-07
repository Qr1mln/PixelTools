import logging

from api import Color
from api.Debug import Debug
from api.Window import Window

logging.basicConfig(level=logging.INFO)


class PTPlugin(Window,Color,Debug):
    _version = "1.0.0"
    hwnd = 0
    is_bind = 0
    ox = 0
    oy = 0
    def __init__(self):
        super().__init__()
        ...

