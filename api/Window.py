import logging

import win32gui
logging.basicConfig(level=logging.INFO)

class Window:
    def __init__(self):
       ...

    def bind(self, hwnd: int=0,title: str|None=None,clazz:str|None=None, display: str="normal", mouse: str="normal", keypad: str="normal", mode: int=0)-> bool:
        """
         * BindWindow - 绑定窗口
         * 功能：绑定指定窗口，并设置图色、鼠标、键盘仿真模式及绑定模式。
         * 说明：BindWindowEx 的简易版；部分模式/功能为付费功能。
         *
         * 语法：
         *   结果 = dm.BindWindow(窗口句柄, 图色属性, 鼠标属性, 键盘属性, 模式)
         *
         * 参数：
         *   窗口句柄  整型    待绑定的窗口句柄
         *   图色属性  字符串  normal / gdi / gdi2 / dx2 / dx3 / dx
         *   鼠标属性  字符串  normal / windows / windows2 / windows3 / dx / dx2
         *   键盘属性  字符串  normal / windows / dx
         *   模式      整型    0 推荐；2 同0，崩溃可试；4 免费版独有；
         *                    101/103 付费超级绑定；11/13 付费驱动模式，不支持32位
         *
         * 返回：
         *   逻辑  False 失败，True 成功；失败可调用 GetLastError 查看错误码
         *
         * 注意：
         *   1. 0/2 模式主绑定线程需一致且持续存活，否则绑定会消失。
         *   2. dx 类鼠标/键盘模式可能需要先激活窗口再绑定。
         *   3. 101/103 对多子窗口窗口，建议先激活可输入文字的文本框。
         """
        ...
        # 如果指定hwnd，直接查找对应窗口。
        # 否则 根据标题、类名组合搜索，返回窗口。
        if not hwnd:
            hwnd = win32gui.FindWindow(clazz, title)

        if not win32gui.IsWindow(hwnd):
            logging.error(f"窗口句柄无效: {hwnd}")
            return False

        setattr(self, "hwnd", hwnd)
        # 获取窗口信息

        top, left, width, height = win32gui.GetWindowRect(hwnd)
        logging.info(f"窗口信息: {top},{left},{width},{height}")

        setattr(self, "ox", top)
        setattr(self, "oy", left)
        return True
