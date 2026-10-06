"""
大漠插件 (DM Plugin) API 模拟层 —— 扁平模块划分版

模块划分 (mixin 方式):
    - base         : 基础 / 窗口绑定模块
    - color        : 颜色模块 (取色/比色/找色/多点找色/颜色统计/平均色)
    - image        : 图像模块 (找图/图片参数/截图与屏幕数据)
    - dictionary   : 字典模块 (字库/OCR/找字)
    - mouse        : 鼠标模块
    - keyboard     : 键盘模块
    - input_control: 输入锁 / 全局控制模块

设计说明:
    - 每个模块是一个独立的类 (mixin), 仅含方法桩与中文注释, 无具体实现。
    - 顶层 PtPlugin 继承全部模块, 对外暴露与大漠一致的扁平方法集合:
          dm = PtPlugin()
          dm.find_pic(...)   # 图像
          dm.find_color(...) # 颜色
          dm.ocr(...)        # 字典
          dm.move_to(...)    # 鼠标
          dm.key_press(...)  # 键盘
    - 返回值约定对齐大漠: int 1/0 成功/失败; str "x|y" 坐标, 未找到返回 ""。
"""

from __future__ import annotations

from .base import BaseModule
from .color import ColorModule
from .dictionary import DictionaryModule
from .image import ImageModule
from .input_control import InputControlModule
from .keyboard import KeyboardModule
from .mouse import MouseModule


class PtPlugin(
    BaseModule,
    ColorModule,
    ImageModule,
    DictionaryModule,
    MouseModule,
    KeyboardModule,
    InputControlModule,
):
    """大漠插件主接口模拟类 (聚合七大模块, 扁平调用风格)。"""

    def __init__(self) -> None:
        super().__init__()


__all__ = [
    "PtPlugin",
    "BaseModule",
    "ColorModule",
    "ImageModule",
    "DictionaryModule",
    "MouseModule",
    "KeyboardModule",
    "InputControlModule",
]
