import time

from api import PtPlugin
from show_result import show_found_points

if __name__ == '__main__':
    pt = PtPlugin()
    print(pt.ver())
    is_bind = pt.bind_window(4135884, "gdi", "windows", "windows", 0)
    print(is_bind)

