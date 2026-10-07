import logging

from api.Color import Color
from api.Debug import Debug
from api.Window import Window

logging.basicConfig(level=logging.INFO)


def version() -> str:
    return PTPlugin.version


class PTPlugin:
    version = "1.0.0"
    hwnd = 0
    is_bind = 0
    ox = 0
    oy = 0
    window = Window
    Color = Color
    def __init__(self):
        ...
