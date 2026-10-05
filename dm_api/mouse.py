"""鼠标模块 (Mouse) —— 大漠 API 模拟桩。"""

from __future__ import annotations

from typing import Any


class MouseModule:
    """鼠标相关方法 (大漠 API 模拟桩)。"""

    def MoveTo(self, x: int, y: int) -> int:
        """移动鼠标到指定绝对坐标。"""
        ...

    def MoveR(self, dx: int, dy: int) -> int:
        """相对当前位置移动鼠标 (dx, dy 可为负)。"""
        ...

    def LeftClick(self) -> int:
        """鼠标左键单击 (按下+抬起)。"""
        ...

    def LeftDown(self) -> int:
        """鼠标左键按下 (不抬起)。"""
        ...

    def LeftUp(self) -> int:
        """鼠标左键抬起。"""
        ...

    def RightClick(self) -> int:
        """鼠标右键单击。"""
        ...

    def RightDown(self) -> int:
        """鼠标右键按下。"""
        ...

    def RightUp(self) -> int:
        """鼠标右键抬起。"""
        ...

    def MiddleClick(self) -> int:
        """鼠标中键单击。"""
        ...

    def MiddleDown(self) -> int:
        """鼠标中键按下。"""
        ...

    def MiddleUp(self) -> int:
        """鼠标中键抬起。"""
        ...

    def WheelDown(self, lines: int = 1) -> int:
        """鼠标滚轮向下滚动。"""
        ...

    def WheelUp(self, lines: int = 1) -> int:
        """鼠标滚轮向上滚动。"""
        ...

    def LeftDoubleClick(self) -> int:
        """鼠标左键双击。"""
        ...

    def RightDoubleClick(self) -> int:
        """鼠标右键双击。"""
        ...

    def GetCursorPos(self) -> str:
        """获取当前鼠标位置, 返回 "x|y"。"""
        ...

    def GetMousePoint(self) -> str:
        """获取鼠标所在位置的颜色点信息 (常用于辅助调试)。"""
        ...

    def GetMousePointWindow(self) -> int:
        """获取鼠标当前所在位置的窗口句柄。"""
        ...

    def GetCursorShape(self) -> str:
        """获取当前鼠标光标形状数据 (base64)。"""
        ...

    def GetCursorBunch(self) -> str:
        """获取当前鼠标光标的相关信息组。"""
        ...

    def MatchCursor(self, shape: str) -> int:
        """匹配当前鼠标光标形状 (用于判断特定状态)。"""
        ...

    def SetMouseDelay(self, delay: int) -> int:
        """设置鼠标操作之间的延时 (毫秒)。"""
        ...

    def SetMouseSpeed(self, speed: int) -> int:
        """设置鼠标移动速度 (0~100, 越大越快)。"""
        ...

    def GetMouseSpeed(self) -> int:
        """获取当前鼠标移动速度。"""
        ...

    def EnableMouseSync(self, mode: int) -> int:
        """开启/关闭鼠标操作同步 (用于某些游戏防检测)。"""
        ...

    def EnableMouseAccuracy(self, mode: int) -> int:
        """开启/关闭鼠标高精度模式。"""
        ...

    def EnableRealMouse(self, en: int, x: int = 1, y: int = 1) -> int:
        """开启/关闭真实鼠标模拟 (带随机轨迹, 防检测)。"""
        ...

    def SetMouseTrail(self, *args: Any) -> int:
        """设置鼠标移动轨迹特征 (增强真实感)。"""
        ...
