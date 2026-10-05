"""键盘模块 (Keyboard) —— 大漠 API 模拟桩。"""

from __future__ import annotations


class KeyboardModule:
    """键盘相关方法 (大漠 API 模拟桩)。"""

    def KeyPress(self, key: int) -> int:
        """按下并抬起指定按键 (一次点击)。key 为 vk 码。"""
        ...

    def KeyDown(self, key: int) -> int:
        """按下指定按键 (保持按住)。"""
        ...

    def KeyUp(self, key: int) -> int:
        """抬起指定按键。"""
        ...

    def KeyPressChar(self, key_str: str) -> int:
        """按下并抬起一个用字符表示的按键 (如 "a", "A", "1")。"""
        ...

    def KeyPressStr(self, key_str: str) -> int:
        """逐字符模拟输入一串字符串 (如 "hello123")。"""
        ...

    def KeyPressHex(self, key_str: str) -> int:
        """以十六进制 vk 码形式按下并抬起按键 (如 "41" 表示 A)。"""
        ...

    def WaitKey(self, key: int, timeout: int) -> int:
        """
        等待指定按键被按下。
        :param timeout: 超时时间 (毫秒)。
        :return: 1 在超时前按下, 0 超时。
        """
        ...

    def SetKeypadDelay(self, type_: str, delay: int) -> int:
        """
        设置键盘延时。
        :param type_: "press" / "down" / "up"。
        """
        ...

    def EnableKeyboardSync(self, mode: int) -> int:
        """开启/关闭键盘操作同步。"""
        ...

    def EnableRealKeypad(self, en: int) -> int:
        """开启/关闭真实键盘模拟 (防检测)。"""
        ...
