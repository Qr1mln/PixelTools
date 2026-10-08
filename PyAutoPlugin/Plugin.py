from PyAutoPlugin import Color
from PyAutoPlugin.Debug import Debug
from PyAutoPlugin.Ocr import Ocr
from PyAutoPlugin.Window import Window

class Plugin(Window, Color, Ocr, Debug):
    _version = "1.0.0"
    hwnd = 0
    is_bind = 0
    ox = 0
    oy = 0
    def __init__(self):
        super().__init__()
        ...

