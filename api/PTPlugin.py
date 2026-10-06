from api.Window import Window


class PTPlugin(Window):
    def __init__(self):
        super().__init__()
        self._version = "1.0.0"
        self._hwnd = 0
        self._ox = 0
        self._oy = 0

    def version(self) -> str:
        return self._version