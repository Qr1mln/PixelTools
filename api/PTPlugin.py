import logging

from api.Color import Color
from api.Debug import Debug
from api.Window import Window

logging.basicConfig(level=logging.INFO)
class PTPlugin(Window, Color, Debug):
    def __init__(self):
        super().__init__()
        self._version = "1.0.0"
        self.hwnd = 0
        self.ox = 0
        self.oy = 0

    def version(self) -> str:
        return self._version

