import cv2
import numpy as np


def parse_color_string(s):
    """
    "123456-000000|aabbcc-202020"
      -> [((0x12,0x34,0x56), (0x00,0x00,0x00)),
          ((0xaa,0xbb,0xcc), (0x20,0x20,0x20))]
    若某项没写偏色，默认 (0,0,0)
    """
    result = []
    for item in s.split('|'):
        item = item.strip()
        if not item:
            continue
        if '-' in item:
            main_hex, off_hex = item.split('-', 1)
        else:
            main_hex, off_hex = item, '000000'

        rgb = tuple(int(main_hex[i:i + 2], 16) for i in (0, 2, 4))
        off = tuple(int(off_hex[i:i + 2], 16) for i in (0, 2, 4))
        result.append((rgb, off))
    return result


def multi_color_mask(region_rgb, color_str):
    """
    region_rgb : (h, w, 3) RGB
    color_str  : "123456-000000|aabbcc-202020"
    返回 mask  : (h, w) uint8，命中任意一项为 255
    """
    entries = parse_color_string(color_str)
    h, w = region_rgb.shape[:2]
    combined = np.zeros((h, w), dtype=np.uint8)

    for target_rgb, offset_rgb in entries:
        t = np.array(target_rgb, dtype=np.int16)
        o = np.array(offset_rgb, dtype=np.int16)

        lower = np.clip(t - o, 0, 255).astype(np.uint8)
        upper = np.clip(t + o, 0, 255).astype(np.uint8)

        m = cv2.inRange(region_rgb, lower, upper)  # 逐通道容差
        combined = cv2.bitwise_or(combined, m)  # 累积命中

    return combined

class Color:
    def __init__(self):
        ...
    @staticmethod
    def findColor(x1, y1, x2, y2, color, sim=None, mode=0)-> tuple[int, int]:
        """
        函数简介:

        查找指定区域内的颜色,颜色格式"RRGGBB-DRDGDB",注意,和按键的颜色格式相反

        函数原型:

        long FindColor(x1, y1, x2, y2, color, sim, dir,intX,intY)

        参数定义:

        x1 整形数:区域的左上X坐标
        y1 整形数:区域的左上Y坐标
        x2 整形数:区域的右下X坐标
        y2 整形数:区域的右下Y坐标
        color 字符串:颜色 格式为"RRGGBB-DRDGDB",比如"123456-000000|aabbcc-202020". 也可以支持反色模式. 前面加@即可. 比如"@123456-000000|aabbcc-202020". 具体可以看下放注释. 注意，这里只支持RGB颜色.
        sim 双精度浮点数:相似度,取值范围0.1-1.0
        mode 整形数:查找方向 0: 从左到右,从上到下
                     1: 从左到右,从下到上
                     2: 从右到左,从上到下
                     3: 从右到左,从下到上
                     4：从中心往外查找
                     5: 从上到下,从左到右
                     6: 从上到下,从右到左
                     7: 从下到上,从左到右
                     8: 从下到上,从右到左
        intX 变参指针:返回X坐标
        intY 变参指针:返回Y坐标

        返回值: (x, y) 命中坐标；未找到返回 (-1, -1)
        :return: tuple[int, int]
        """

        # 统一转成"主色-偏色"字符串形式
        if isinstance(color, str):
            color_str = color
        elif isinstance(color, (tuple, list)):
            color_str = '%02X%02X%02X-000000' % tuple(color)
        else:
            raise ValueError('color 格式错误')
        # 裁剪非法坐标后，直接截客户区矩形。
        # screenshot 内部已用 ClientToScreen 完成 DPI 映射，无需手动修正。
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = max(x1, x2)
        y2 = max(y1, y2)
        # screenshot 实际在 Window 上，惰性导入避免与 PTPlugin/Color 的循环依赖
        from api import PTPlugin
        img_rgb = PTPlugin.window.screenshot(x1, y1, x2, y2)  # (H, W, 3) RGB
        H, W = img_rgb.shape[:2]
        if H == 0 or W == 0:
            return -1, -1

        region = img_rgb  # 整张即为目标区域，不再二次裁切

        # 偏色掩码
        mask = multi_color_mask(region, color_str)

        # 可选：额外 sim 过滤
        if sim is not None:
            # 取第一项的 target 做相似度过滤（多色时按需要可改）
            first_rgb, _ = parse_color_string(color_str)[0]
            target = np.array(first_rgb, dtype=np.int16)
            diff_sum = np.sum(cv2.absdiff(region.astype(np.int16), target), axis=2)
            sims = 1.0 - diff_sum / 765.0
            sim_mask = np.where(sims >= sim, 255, 0).astype(np.uint8)
            mask = cv2.bitwise_and(mask, sim_mask)

        if not mask.any():
            return -1, -1

        # 按 mode 找第一个点
        ys, xs = np.where(mask > 0)
        h, w = mask.shape

        if mode == 0:
            idx = np.argmin(ys * w + xs)
        elif mode == 1:
            idx = np.argmin((h - ys) * w + xs)
        elif mode == 2:
            idx = np.argmin(ys * w + (w - xs))
        else:
            idx = np.argmin((h - ys) * w + (w - xs))

        return int(xs[idx]), int(ys[idx])

    """
    FindMultiColor 的最大优势是：不依赖图片，靠多点颜色特征定位，速度快、误判低、抗干扰强，特别适合游戏/自动化脚本里找动态或半透明的 UI 元素。
    前提是：特征点要选得稳定、独特、高对比，偏色和相似度也要调得合理。。
    """

    @staticmethod
    def find_multi_color(cls,x1, y1, x2, y2, first_color,offset_color, sim=None, mode=0)-> tuple[int, int]:
        """
        函数简介:

        根据指定的多点查找颜色坐标

        函数原型:

        long FindMultiColor(x1, y1, x2, y2,first_color,offset_color,sim, mode)

        参数定义:

        x1 整形数:区域的左上X坐标
        y1 整形数:区域的左上Y坐标
        x2 整形数:区域的右下X坐标
        y2 整形数:区域的右下Y坐标
        first_color 字符串:颜色格式为"RRGGBB-DRDGDB|RRGGBB-DRDGDB|…………",比如"123456-000000"

        这里的含义和按键自带Color插件的意义相同，只不过我的可以支持偏色和多种颜色组合

        所有的偏移色坐标都相对于此颜色.注意，这里只支持RGB颜色.
        offset_color 字符串: 偏移颜色可以支持任意多个点 格式和按键自带的Color插件意义相同, 只不过我的可以支持偏色和多种颜色组合

         格式为"x1|y1|RRGGBB-DRDGDB|RRGGBB-DRDGDB……,……xn|yn|RRGGBB-DRDGDB|RRGGBB-DRDGDB……"

        比如"1|3|aabbcc|aaffaa-101010,-5|-3|123456-000000|454545-303030|565656"等任意组合都可以，支持偏色

        sim 双精度浮点数:相似度,取值范围0.1-1.0
        mode 整形数:查找方向 0: 从左到右,从上到下 1: 从左到右,从下到上 2: 从右到左,从上到下 3: 从右到左, 从下到上

        返回值:
        """

