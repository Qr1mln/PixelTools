import time

from api import PTPlugin, Debug

if __name__ == '__main__':
    is_bind = PTPlugin.bind_window(title="Last Epoch", clazz="UnityWndClass")
    x,y = PTPlugin.findColor(446, 979, 575, 997, "ffffff-000000")
    print(x,y)
    print(is_bind)
    # Debug.preview(PTPlugin.screenshot(446,979,575,997),"test",x,y,color=(0,255,0))
    img = PTPlugin.screenshot(849,947,1049,1047)
    #x,y = PTPlugin.findMultiColor(845, 948, 1045, 1048, "e9e8e8-000000", "-33|-11|7d7a7c,48|-9|6e6a6d,6|6|18031a")
    points = PTPlugin.findMultiColorEx(849,947,1049,1047,"e9e8e8-000000","-33|-11|7d7a7c,48|-9|6e6a6d,6|6|18031a",
    sim=0.9)
    print(points)
    #PTPlugin.preview(img,"test",x,y)
    PTPlugin.preview(img,"test",points =points)
    PTPlugin.unbind_window()

