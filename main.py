import time

from api import PTPlugin

if __name__ == '__main__':
    pt = PTPlugin()
    print(pt.version())
    is_bind = pt.bind_window(title="Last Epoch", clazz="UnityWndClass")
    print(is_bind)

