"""
字典模块 (Dictionary) —— 大漠 API 模拟桩。

涵盖: 字库管理 / OCR 文字识别 / 基于字库的找字。

参数约定:
    - (x1,y1,x2,y2): 矩形区域左上角与右下角 (闭区间)。
    - color: 文字颜色 "RRGGBB" 或范围。
    - sim:   相似度 0.0~1.0。
    - index: 字库索引 (0~9)。
"""

from __future__ import annotations

from typing import Any


class DictionaryModule:
    """字库与 OCR 相关方法 (大漠 API 模拟桩)。"""

    def set_dict(self, index: int, file: str) -> int:
        """
        设置字库文件。
        :param index: 字库索引 (0~9)。
        :param file:  字库文件名 (相对于 set_path 目录)。
        :return: 1 成功, 0 失败。
        """
        ...

    def use_dict(self, index: int) -> int:
        """切换到指定索引的字库。"""
        ...

    def get_dict_count(self, index: int) -> int:
        """获取指定字库中的词条数量。"""
        ...

    def ocr(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
    ) -> str:
        """
        在区域内进行文字识别 (OCR), 返回识别出的字符串; 失败返回 ""。
        :param color: 文字颜色 "RRGGBB" 或范围。
        :param sim:   相似度。
        """
        ...

    def ocr_ex(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
    ) -> str:
        """ocr 的扩展版, 返回带坐标的结果 "文本|x|y|w|h|..."。"""
        ...

    def ocr_auto(self, x1: int, y1: int, x2: int, y2: int, flag: int) -> str:
        """
        自动二值化 OCR (无需字库也能识别常见文字)。
        :param flag: 二值化/识别参数标志位。
        """
        ...

    def ocr_auto_ex(self, x1: int, y1: int, x2: int, y2: int, flag: int) -> str:
        """ocr_auto 的扩展版, 返回带坐标结果。"""
        ...

    def ocr_from_file(self, file: str, color: str, sim: float) -> str:
        """对图片文件进行 OCR 识别。"""
        ...

    def find_str(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        str_: str,
        color: str,
        sim: float,
    ) -> str:
        """
        在区域内查找指定字符串 (基于字库)。
        :param str_: 待查找字符串 (支持 "|" 分隔的多个候选)。
        :return: "x|y" 或 ""。
        """
        ...

    def find_str_ex(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        str_: str,
        color: str,
        sim: float,
    ) -> str:
        """find_str 的全区域版本, 返回所有匹配点。"""
        ...

    def find_str_fast(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        str_: str,
        color: str,
        sim: float,
    ) -> str:
        """find_str 的快速版 (适用于大区域/大字典)。"""
        ...

    def find_str_fast_ex(self, *args: Any) -> str:
        """find_str_fast 的全区域版本。"""
        ...

    def find_str_s(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        str_: str,
        color: str,
        sim: float,
        dir_: int,
        timeout: int,
    ) -> str:
        """带超时的持续找字。"""
        ...

    def find_str_sim(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        str_: str,
        color: str,
        sim: float,
        dir_: int,
        timeout: int,
        s_type: int,
    ) -> str:
        """find_str_s 的扩展版, 支持相似度类型。"""
        ...

    def find_str_sim_ex(self, *args: Any) -> str:
        """find_str_sim 的全区域版本。"""
        ...

    def get_words(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
    ) -> str:
        """获取区域内所有识别到的词 (带字库), 返回 "词1|词2|..."。"""
        ...

    def get_words_no_dict(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
    ) -> str:
        """get_words 的无字库版本。"""
        ...

    def get_words_rate(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
    ) -> str:
        """获取区域内文字及其识别置信度。"""
        ...
