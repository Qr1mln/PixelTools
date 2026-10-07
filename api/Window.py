import logging

import cv2
import numpy as np
import win32gui
from mss import MSS
from numpy._typing import NDArray

from api import dpi, PTPlugin

class Window:
    def __init__(self):
        ...

    @classmethod
    def screenshot(cls, x1: int | None = None, y1: int | None = None, x2: int | None = None, y2: int | None = None) -> NDArray[np.float64]:
        """
        全屏截图或指定区域截图，返回 (H, W, 3) 的 RGB numpy 数组。
        ox, oy: 客户端左上角在屏幕上的坐标


        参数:
        x1, y1: 左上角坐标 (可选)
        x2, y2: 右下角坐标 (可选)
        若全部为 None，则截取主显示器全屏。
        """
        """返回 RGB ndarray，可写。"""
        with MSS() as sct:
            mon = sct.monitors[1]
            # 如果没有指定坐标，则截取主显示器全屏。
            if x1 is None or y1 is None or x2 is None or y2 is None:
                region = {"left": mon["left"], "top": mon["top"],
                          "width": mon["width"], "height": mon["height"]}
            else:
                # DPI 感知已开启，ClientToScreen 直接把客户区逻辑坐标映射到物理屏幕坐标，
                # 系统已自动完成 DPI 缩放换算，无需手动乘 scale。
                hwnd = PTPlugin.hwnd
                p1 = win32gui.ClientToScreen(hwnd, (x1, y1))
                p2 = win32gui.ClientToScreen(hwnd, (x2, y2))
                sx1, sy1 = p1
                sx2, sy2 = p2
                logging.info(f"屏幕坐标: ({sx1},{sy1}) - ({sx2},{sy2})")

                left = max(min(sx1, sx2), mon["left"])
                top = max(min(sy1, sy2), mon["top"])
                right = min(max(sx1, sx2), mon["left"] + mon["width"])
                bottom = min(max(sy1, sy2), mon["top"] + mon["height"])
                w = right - left
                h = bottom - top
                if w <= 0 or h <= 0:
                    return np.zeros((0, 0, 3), dtype=np.uint8)
                region = {"left": left, "top": top, "width": w, "height": h}

            shot = sct.grab(region)
            rgb = np.frombuffer(shot.rgb, dtype=np.uint8).reshape(shot.height, shot.width, 3)
            return np.array(rgb, copy=True)  # 可写 RGB

    @classmethod
    def bind_window(cls, hwnd: int = 0, title: str | None = None, clazz: str | None = None, display: str = "normal",
                    mouse: str = "normal", keypad: str = "normal", mode: int = 0) -> bool:
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

        # 进程需 DPI 感知，保证 ClientToScreen / mss 坐标统一为物理像素
        dpi.set_dpi_aware()

        PTPlugin.hwnd = hwnd
        # 获取窗口信息

        # 客户区左上角在屏幕上的物理像素坐标（仅供信息/参考）
        cx, cy = dpi.get_client_origin_physical(hwnd)
        logging.info(f"客户区原点(物理): {cx},{cy}")
        PTPlugin.ox = cx
        PTPlugin.oy = cy
        PTPlugin.is_bind = 1
        return True

    @classmethod
    def unbind_window(cls):
        """
        取消绑定窗口
        :return:
        """
        PTPlugin.hwnd = 0
        PTPlugin.ox = 0
        PTPlugin.oy = 0
        PTPlugin.is_bind = 0