"""输入锁 / 全局控制模块 (Input Control) —— 大漠 API 模拟桩。"""

from __future__ import annotations


class InputControlModule:
    """输入锁与全局控制相关方法 (大漠 API 模拟桩)。"""

    def lock_input(self, state: int) -> int:
        """锁定/解锁输入 (防止操作期间用户干扰)。1 锁定, 0 解锁。"""
        ...

    def lock_display(self, state: int) -> int:
        """锁定/解锁显示输出。"""
        ...
