import time

from api import PTPlugin

if __name__ == '__main__':
    pt = PTPlugin()
    print(pt.version())
    is_bind = pt.bind_window(4135884, "gdi", "windows", "windows", 0)
    print(is_bind)

