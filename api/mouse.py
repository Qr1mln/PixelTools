"""鼠标模块 (Mouse) —— 大漠 API 模拟桩。"""

from __future__ import annotations

from typing import Any

# 已知的后台鼠标模式 (windows2 / dx 系列), 需要大漠驱动, 本项目暂留桩
_BACKGROUND_MOUSE_MODES = {"windows2", "dx", "dx2", "dx3", "dx2.0"}


class MouseModule:
    """鼠标相关方法 (大漠 API 模拟桩)。"""

    def _is_background_mouse(self) -> bool:
        """当前绑定的 mouse 模式是否属于需要驱动的后台模式 (暂未实现)。"""
        return getattr(self, "_mouse", "") in _BACKGROUND_MOUSE_MODES

    def move_to(self, x: int, y: int) -> bool:
        """移动鼠标到指定绝对坐标 (前台真实事件; 后台/dx 模式暂留桩)。

        坐标基于绑定窗口客户区左上角; 若已 bind, 会自动换算为屏幕坐标。
        :return: 移动成功 True, 失败 False (后台模式返回 False 表示暂未实现)。
        """
        import win32api  # 现成包 pywin32: 设置光标位置

        # 后台/dx 模式需要大漠驱动, 暂留桩
        if self._is_background_mouse():
            return False

        ox, oy = getattr(self, "_client_origin", (0, 0))
        try:
            win32api.SetCursorPos((ox + x, oy + y))
            return True
        except Exception:
            return False

    def move_rel(self, dx: int, dy: int) -> bool:
        """相对当前位置移动鼠标 (dx, dy 可为负); 仅前台模式, 后台留桩。

        :return: 移动成功 True, 失败 False (后台模式返回 False 表示暂未实现)。
        """
        import win32api  # 现成包 pywin32: 光标位置获取/设置

        # 后台/dx 模式需要大漠驱动, 暂留桩
        if self._is_background_mouse():
            return False

        try:
            cx, cy = win32api.GetCursorPos()
            win32api.SetCursorPos((cx + dx, cy + dy))
            return True
        except Exception:
            return False

    def left_click(self) -> int:
        """鼠标左键单击 (按下+抬起)。"""
        ...

    def left_down(self) -> int:
        """鼠标左键按下 (不抬起)。"""
        ...

    def left_up(self) -> int:
        """鼠标左键抬起。"""
        ...

    def right_click(self) -> int:
        """鼠标右键单击。"""
        ...

    def right_down(self) -> int:
        """鼠标右键按下。"""
        ...

    def right_up(self) -> int:
        """鼠标右键抬起。"""
        ...

    def middle_click(self) -> int:
        """鼠标中键单击。"""
        ...

    def middle_down(self) -> int:
        """鼠标中键按下。"""
        ...

    def middle_up(self) -> int:
        """鼠标中键抬起。"""
        ...

    def wheel_down(self, lines: int = 1) -> int:
        """鼠标滚轮向下滚动。"""
        ...

    def wheel_up(self, lines: int = 1) -> int:
        """鼠标滚轮向上滚动。"""
        ...

    def left_double_click(self) -> int:
        """鼠标左键双击。"""
        ...

    def right_double_click(self) -> int:
        """鼠标右键双击。"""
        ...

    def get_cursor_pos(self) -> str:
        """获取当前鼠标位置, 返回 "x|y"。"""
        ...

    def get_mouse_point(self) -> str:
        """获取鼠标所在位置的颜色点信息 (常用于辅助调试)。"""
        ...

    def get_mouse_point_window(self) -> int:
        """获取鼠标当前所在位置的窗口句柄。"""
        ...

    def get_cursor_shape(self) -> str:
        """获取当前鼠标光标形状数据 (base64)。"""
        ...

    def get_cursor_bunch(self) -> str:
        """获取当前鼠标光标的相关信息组。"""
        ...

    def match_cursor(self, shape: str) -> int:
        """匹配当前鼠标光标形状 (用于判断特定状态)。"""
        ...

    def set_mouse_delay(self, delay: int) -> int:
        """设置鼠标操作之间的延时 (毫秒)。"""
        ...

    def set_mouse_speed(self, speed: int) -> int:
        """设置鼠标移动速度 (0~100, 越大越快)。"""
        ...

    def get_mouse_speed(self) -> int:
        """获取当前鼠标移动速度。"""
        ...

    def enable_mouse_sync(self, mode: int) -> int:
        """开启/关闭鼠标操作同步 (用于某些游戏防检测)。"""
        ...

    def enable_mouse_accuracy(self, mode: int) -> int:
        """开启/关闭鼠标高精度模式。"""
        ...

    def enable_real_mouse(self, en: int, x: int = 1, y: int = 1) -> int:
        """开启/关闭真实鼠标模拟 (带随机轨迹, 防检测)。"""
        ...

    def set_mouse_trail(self, *args: Any) -> int:
        """设置鼠标移动轨迹特征 (增强真实感)。"""
        ...
