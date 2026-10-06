from api.Window import Window


class PTPlugin(Window):
    def __init__(self):
        super().__init__()
        self.version = "1.0.0"
        self.hwnd = 0
        self.ox = 0
        self.oy = 0

    def version(self) -> str:
        return self.version