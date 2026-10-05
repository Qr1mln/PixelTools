"""
大漠插件 (DM Plugin) API 模拟层 —— 模块化版本

模块划分:
    - base          : 基础 / 窗口绑定模块
    - image_color   : 图色模块 (取色/找色/找图/OCR/找字/截图)
    - mouse         : 鼠标模块
    - keyboard      : 键盘模块
    - input_control : 输入锁 / 全局控制模块

设计说明:
    - 采用 mixin (混入类) 方式: 每个模块是一个独立的类, 仅含方法桩与中文注释, 无具体实现。
    - 顶层 DmPlugin 继承全部模块, 因此仍保持大漠"扁平"调用风格:
          dm = DmPlugin()
          dm.FindPic(...)   # 图色
          dm.MoveTo(...)    # 鼠标
          dm.KeyPress(...)  # 键盘
    - 后续实现时, 可在各模块文件中填充真实逻辑 (互不干扰, 便于维护)。

返回值约定 (对齐大漠):
    - int  : 成功 1 / 失败 0; 部分方法返回计数或坐标分量。
    - str  : 找到时返回 "x|y" / "x|y|..."; 未找到返回 "" (空字符串)。
    - 屏幕左上角为 (0, 0)。
"""

from __future__ import annotations

from .base import BaseModule
from .image_color import ImageColorModule
from .mouse import MouseModule
from .keyboard import KeyboardModule
from .input_control import InputControlModule


class PtPlugin(
    BaseModule,
    ImageColorModule,
    MouseModule,
    KeyboardModule,
    InputControlModule,
):
    """
    大漠插件主接口模拟类。

    聚合了 base / image_color / mouse / keyboard / input_control 五大模块,
    对外暴露与大漠插件一致的扁平方法集合。实例化后即可调用任意模块的方法。
    """

    def __init__(self) -> None:
        # 预留: 真实实现时可在各模块中挂载底层后端 (截图器/输入模拟器等)。
        super().__init__()


__all__ = [
    "PtPlugin",
    "BaseModule",
    "ImageColorModule",
    "MouseModule",
    "KeyboardModule",
    "InputControlModule",
]
