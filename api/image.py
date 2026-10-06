"""
图像模块 (Image) —— 大漠 API 模拟桩。

涵盖: 找图 (文件/内存/地址) / 图片参数设置 / 截图与屏幕数据。

参数约定:
    - (x1,y1,x2,y2): 矩形区域左上角与右下角 (闭区间)。
    - pic_name: 图片文件名 (相对于 set_path 目录), 多图用 "|" 分隔。
    - delta_color: 颜色偏差, 如 "000000" 或 "RRGGBB-DRRDGGDBB"。
    - sim:      相似度 0.0~1.0。
"""

from __future__ import annotations

from typing import Any


class ImageModule:
    """图像相关方法 (大漠 API 模拟桩)。"""

    def find_pic(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        pic_name: str,
        delta_color: str,
        sim: float,
        dir_: int = 0,
    ) -> str:
        """
        在区域内查找图片 (支持多个, 用 "|" 分隔文件名)。
        :param pic_name:    图片文件名 (相对于 set_path 目录), 多图用 "|" 分隔。
        :param delta_color: 颜色偏差, 如 "000000" 或 "RRGGBB-DRRDGGDBB"。
        :param sim:         相似度。
        :return: "x|y" 或 ""。
        """
        ...

    def find_pic_ex(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        pic_name: str,
        delta_color: str,
        sim: float,
        dir_: int = 0,
    ) -> str:
        """find_pic 的全区域版本, 返回所有匹配点 "x1|y1|x2|y2|..."。"""
        ...

    def find_pic_mem(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        pic_info: str,
        delta_color: str,
        sim: float,
        dir_: int = 0,
    ) -> str:
        """从内存数据 (base64 编码的图片) 中找图, 返回 "x|y"。"""
        ...

    def find_pic_mem_ex(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        pic_info: str,
        delta_color: str,
        sim: float,
        dir_: int = 0,
    ) -> str:
        """find_pic_mem 的全区域版本, 返回所有匹配点。"""
        ...

    def find_pic_s(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        pic_name: str,
        delta_color: str,
        sim: float,
        dir_: int,
        timeout: int,
    ) -> str:
        """带超时的持续找图 (在 timeout 毫秒内反复尝试), 返回 "x|y"。"""
        ...

    def find_pic_sim(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        pic_name: str,
        delta_color: str,
        sim: float,
        dir_: int,
        timeout: int,
        s_type: int,
    ) -> str:
        """find_pic_s 的扩展版, 支持指定相似度类型 s_type。"""
        ...

    def find_pic_addr(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        pic_info: str,
        delta_color: str,
        sim: float,
        dir_: int = 0,
    ) -> str:
        """从内存地址 (图片数据指针) 中找图, 返回 "x|y"。"""
        ...

    def find_pic_addr_ex(self, *args: Any) -> str:
        """find_pic_addr 的全区域版本。"""
        ...

    def get_pic_size(self, pic_name: str) -> str:
        """获取图片尺寸, 返回 "width|height"。"""
        ...

    def retry_find_pic(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        pic_name: str,
        delta_color: str,
        sim: float,
        dir_: int,
        timeout: int,
        retry: int,
        delay: int,
    ) -> str:
        """在 timeout+retry+delay 组合下重试找图。"""
        ...

    def set_pic_find_scale(self, scale: float) -> int:
        """设置找图的缩放比例 (用于不同分辨率适配)。"""
        ...

    def set_pic_find_threshold(self, threshold: float) -> int:
        """设置找图的阈值上限。"""
        ...

    def enable_pic_cache(self, enable: int) -> int:
        """开启/关闭图片缓存 (1 开启, 0 关闭), 提升重复找图性能。"""
        ...

    def set_cut_img_mode(self, mode: int) -> int:
        """设置图片裁剪模式 (针对部分游戏截图黑边的处理)。"""
        ...

    def capture(self, x1: int, y1: int, x2: int, y2: int, file: str) -> int:
        """将指定区域截图保存为 BMP 文件。1 成功, 0 失败。"""
        ...

    def capture_png(self, x1: int, y1: int, x2: int, y2: int, file: str) -> int:
        """将指定区域截图保存为 PNG 文件。"""
        ...

    def capture_jpg(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        file: str,
        quality: int = 80,
    ) -> int:
        """将指定区域截图保存为 JPG 文件, quality 为压缩质量 (0~100)。"""
        ...

    def capture_memory(self, *args: Any) -> Any:
        """将截图保存到内存并返回其句柄/数据。"""
        ...

    def get_screen_data(self, x1: int, y1: int, x2: int, y2: int) -> Any:
        """获取屏幕区域的原始像素数据 (Variant 数组)。"""
        ...

    def get_screen_data_bmp(self, x1: int, y1: int, x2: int, y2: int) -> Any:
        """获取屏幕区域的 BMP 内存数据。"""
        ...
