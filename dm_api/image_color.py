"""
图色模块 (Image / Color) —— 大漠 API 模拟桩。

涵盖: 取色比色 / 找色 / 多点找色 / 找图 / 找图参数 / 字库与 OCR / 找字 / 截图与屏幕数据。

参数约定:
    - (x1,y1,x2,y2): 矩形区域左上角与右下角 (闭区间)。
    - color: 十六进制颜色字符串, 默认格式 "RRGGBB"。
    - sim:   相似度 0.0~1.0, 越大越严格。
    - dir:   查找方向 (0=左上->右下, 1=中心->四周, 2=右下->左上 ...)。
"""

from __future__ import annotations

from typing import Any


class ImageColorModule:
    """图色相关方法 (大漠 API 模拟桩)。"""

    # =================================================================
    # 取色 / 比色
    # =================================================================

    def GetColor(self, x: int, y: int) -> str:
        """获取指定坐标的颜色, 返回 "RRGGBB" 格式字符串。"""
        ...

    def GetColorBGR(self, x: int, y: int) -> str:
        """获取指定坐标颜色 (BGR 顺序), 返回 "BBGGRR"。"""
        ...

    def GetColorHSV(self, x: int, y: int) -> str:
        """获取指定坐标颜色的 HSV 值, 返回 "h|s|v"。"""
        ...

    def GetPixelColor(self, x: int, y: int, mode: int = 0) -> str:
        """
        获取指定坐标的像素颜色。
        :param mode: 0=正常, 1=快速 (可能不精确)。
        """
        ...

    def CmpColor(self, x: int, y: int, color: str, sim: float) -> int:
        """
        比较指定坐标的颜色是否与目标颜色相似。
        :param color: 目标颜色 "RRGGBB"。
        :param sim:   相似度 0.0~1.0。
        :return: 1 相似, 0 不相似。
        """
        ...

    def GetColorNum(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
        dir_: int = 0,
    ) -> int:
        """统计指定区域内与 color 相似的颜色数量。"""
        ...

    def GetColorCount(self, *args: Any) -> int:
        """GetColorNum 的别名/扩展, 统计相似颜色出现次数。"""
        ...

    def GetAveRGB(self, x1: int, y1: int, x2: int, y2: int) -> str:
        """获取指定区域的平均 RGB 颜色, 返回 "RRGGBB"。"""
        ...

    def GetAveHSV(self, x1: int, y1: int, x2: int, y2: int) -> str:
        """获取指定区域的平均 HSV, 返回 "h|s|v"。"""
        ...

    # =================================================================
    # 找色
    # =================================================================

    def FindColor(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
        dir_: int = 0,
    ) -> str:
        """
        在区域内查找指定颜色, 返回第一个匹配点 "x|y"; 未找到返回 ""。
        :param color: 目标颜色 "RRGGBB"。
        :param dir_:  查找方向。
        """
        ...

    def FindColorEx(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
        dir_: int = 0,
    ) -> str:
        """查找区域内所有匹配颜色, 返回 "x1|y1|x2|y2|..." 多点字符串。"""
        ...

    def FindColorE(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
        dir_: int = 0,
    ) -> str:
        """FindColor 的增强版, 内部采用更优算法, 返回 "x|y"。"""
        ...

    def FindColorBlock(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
        dir_: int,
        count: int,
    ) -> str:
        """
        查找颜色块 (连续 count 个相似点构成的块)。
        :param count: 颜色块所需的最小像素数。
        :return: "x|y" 或 ""。
        """
        ...

    # =================================================================
    # 多点找色
    # =================================================================

    def FindMultiColor(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        first_color: str,
        offset_color: str,
        sim: float,
        dir_: int = 0,
        color: str = "",
    ) -> str:
        """
        多点找色: 先找 first_color, 再按偏移校验其余颜色。
        :param first_color:  基准颜色 "RRGGBB"。
        :param offset_color: 偏移与颜色串, 如 "1|0|RRGGBB,2|3|112233"。
        :param color:        附加的偏移颜色串 (可空)。
        :return: "x|y" 或 ""。
        """
        ...

    def FindMultiColorEx(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        first_color: str,
        offset_color: str,
        sim: float,
        dir_: int = 0,
        color: str = "",
    ) -> str:
        """FindMultiColor 的全区域版本, 返回所有匹配点 "x1|y1|x2|y2|..."。"""
        ...

    # =================================================================
    # 找图
    # =================================================================

    def FindPic(
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
        :param pic_name:    图片文件名 (相对于 SetPath 目录), 多图用 "|" 分隔。
        :param delta_color: 颜色偏差, 如 "000000" 或 "RRGGBB-DRRDGGDBB"。
        :param sim:         相似度。
        :return: "x|y" 或 ""。
        """
        ...

    def FindPicEx(
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
        """FindPic 的全区域版本, 返回所有匹配点 "x1|y1|x2|y2|..."。"""
        ...

    def FindPicMem(
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

    def FindPicMemEx(
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
        """FindPicMem 的全区域版本, 返回所有匹配点。"""
        ...

    def FindPicS(
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

    def FindPicSim(
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
        """FindPicS 的扩展版, 支持指定相似度类型 s_type。"""
        ...

    def FindPicAddr(
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

    def FindPicAddrEx(self, *args: Any) -> str:
        """FindPicAddr 的全区域版本。"""
        ...

    def GetPicSize(self, pic_name: str) -> str:
        """获取图片尺寸, 返回 "width|height"。"""
        ...

    def RetryFindPic(
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

    def RetryFindColor(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
        dir_: int,
        timeout: int,
        retry: int,
        delay: int,
    ) -> str:
        """在 timeout+retry+delay 组合下重试找色。"""
        ...

    # =================================================================
    # 找图参数控制
    # =================================================================

    def SetPicFindScale(self, scale: float) -> int:
        """设置找图的缩放比例 (用于不同分辨率适配)。"""
        ...

    def SetPicFindThreshold(self, threshold: float) -> int:
        """设置找图的阈值上限。"""
        ...

    def EnablePicCache(self, enable: int) -> int:
        """开启/关闭图片缓存 (1 开启, 0 关闭), 提升重复找图性能。"""
        ...

    def SetCutImgMode(self, mode: int) -> int:
        """设置图片裁剪模式 (针对部分游戏截图黑边的处理)。"""
        ...

    # =================================================================
    # 字库 / 文字识别 (OCR)
    # =================================================================

    def SetDict(self, index: int, file: str) -> int:
        """
        设置字库文件。
        :param index: 字库索引 (0~9)。
        :param file:  字库文件名 (相对于 SetPath 目录)。
        :return: 1 成功, 0 失败。
        """
        ...

    def UseDict(self, index: int) -> int:
        """切换到指定索引的字库。"""
        ...

    def GetDictCount(self, index: int) -> int:
        """获取指定字库中的词条数量。"""
        ...

    def Ocr(
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

    def OcrEx(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
    ) -> str:
        """Ocr 的扩展版, 返回带坐标的结果 "文本|x|y|w|h|..."。"""
        ...

    def OcrAuto(self, x1: int, y1: int, x2: int, y2: int, flag: int) -> str:
        """
        自动二值化 OCR (无需字库也能识别常见文字)。
        :param flag: 二值化/识别参数标志位。
        """
        ...

    def OcrAutoEx(self, x1: int, y1: int, x2: int, y2: int, flag: int) -> str:
        """OcrAuto 的扩展版, 返回带坐标结果。"""
        ...

    def OcrFromFile(self, file: str, color: str, sim: float) -> str:
        """对图片文件进行 OCR 识别。"""
        ...

    # =================================================================
    # 找字
    # =================================================================

    def FindStr(
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

    def FindStrEx(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        str_: str,
        color: str,
        sim: float,
    ) -> str:
        """FindStr 的全区域版本, 返回所有匹配点。"""
        ...

    def FindStrFast(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        str_: str,
        color: str,
        sim: float,
    ) -> str:
        """FindStr 的快速版 (适用于大区域/大字典)。"""
        ...

    def FindStrFastEx(self, *args: Any) -> str:
        """FindStrFast 的全区域版本。"""
        ...

    def FindStrS(
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

    def FindStrSim(
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
        """FindStrS 的扩展版, 支持相似度类型。"""
        ...

    def FindStrSimEx(self, *args: Any) -> str:
        """FindStrSim 的全区域版本。"""
        ...

    def GetWords(
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

    def GetWordsNoDict(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
    ) -> str:
        """GetWords 的无字库版本。"""
        ...

    def GetWordsRate(
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

    # =================================================================
    # 截图 / 屏幕数据
    # =================================================================

    def Capture(self, x1: int, y1: int, x2: int, y2: int, file: str) -> int:
        """将指定区域截图保存为 BMP 文件。1 成功, 0 失败。"""
        ...

    def CapturePng(self, x1: int, y1: int, x2: int, y2: int, file: str) -> int:
        """将指定区域截图保存为 PNG 文件。"""
        ...

    def CaptureJpg(
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

    def CaptureMemory(self, *args: Any) -> Any:
        """将截图保存到内存并返回其句柄/数据。"""
        ...

    def GetScreenData(self, x1: int, y1: int, x2: int, y2: int) -> Any:
        """获取屏幕区域的原始像素数据 (Variant 数组)。"""
        ...

    def GetScreenDataBmp(self, x1: int, y1: int, x2: int, y2: int) -> Any:
        """获取屏幕区域的 BMP 内存数据。"""
        ...
