import time

from api import PTPlugin, Debug

if __name__ == '__main__':
    pt = PTPlugin()
    print(pt.version())
    is_bind = pt.bind_window(title="Last Epoch", clazz="UnityWndClass")
    x,y = pt.findColor(446, 979, 575, 997, "ffffff-000000")
    print(x,y)
    print(is_bind)
    Debug.preview(pt.screenshot(446,979,575,997),"test",x,y,color=(0,255,0))

    pt.unbind_window()

