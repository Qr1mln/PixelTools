from PyAutoPlugin import Plugin

if __name__ == '__main__':
    Plugin.bind_window(title="Last Epoch", clazz="UnityWndClass")
    items = Plugin.ocr(478, 970, 548, 1003)
    Plugin.unbind_window()

