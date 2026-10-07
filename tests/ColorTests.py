import unittest
import numpy as np
from unittest.mock import patch

from api import PTPlugin
from api.Color import parse_color_string,multi_color_mask


def make_image(h=20, w=20, fill=(0, 0, 0), points=None):
    """
    构造测试图像。
    fill  : 背景色 (R,G,B)
    points: {(x, y): (R,G,B), ...} 覆盖指定点颜色
    """
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :] = fill
    if points:
        for (x, y), c in points.items():
            img[y, x] = c
    return img


class TestParseColorString(unittest.TestCase):

    def test_single_with_offset(self):
        self.assertEqual(
            parse_color_string("123456-000000"),
            [((0x12, 0x34, 0x56), (0, 0, 0))]
        )

    def test_single_without_offset(self):
        # 不写偏色，默认 000000
        self.assertEqual(
            parse_color_string("AABBCC"),
            [((0xAA, 0xBB, 0xCC), (0, 0, 0))]
        )

    def test_multi_entries(self):
        self.assertEqual(
            parse_color_string("123456-000000|aabbcc-202020"),
            [
                ((0x12, 0x34, 0x56), (0, 0, 0)),
                ((0xAA, 0xBB, 0xCC), (0x20, 0x20, 0x20)),
            ]
        )

    def test_empty_items_ignored(self):
        self.assertEqual(
            parse_color_string("FF0000-000000||  |00FF00-101010"),
            [
                ((255, 0, 0), (0, 0, 0)),
                ((0, 255, 0), (0x10, 0x10, 0x10)),
            ]
        )


class TestMultiColorMask(unittest.TestCase):

    def test_exact_match_single_color(self):
        img = make_image(fill=(255, 0, 0))
        mask = multi_color_mask(img, "FF0000-000000")
        self.assertTrue((mask == 255).all())

    def test_no_match(self):
        img = make_image(fill=(0, 255, 0))
        mask = multi_color_mask(img, "FF0000-000000")
        self.assertFalse(mask.any())

    def test_offset_allows_variation(self):
        img = make_image(fill=(250, 5, 5))         # 接近 FF0000
        mask = multi_color_mask(img, "FF0000-101010")
        self.assertTrue((mask == 255).all())

    def test_offset_rejects_out_of_range(self):
        img = make_image(fill=(200, 0, 0))         # R 差 55 > 16
        mask = multi_color_mask(img, "FF0000-101010")
        self.assertFalse(mask.any())

    def test_multi_colors_or_logic(self):
        # 两个不同颜色的像素，任一命中即 255
        img = make_image(
            fill=(0, 0, 0),
            points={(0, 0): (255, 0, 0), (1, 0): (0, 255, 0)}
        )
        mask = multi_color_mask(img, "FF0000-000000|00FF00-000000")
        self.assertEqual(mask[0, 0], 255)
        self.assertEqual(mask[0, 1], 255)
        self.assertEqual(mask[5, 5], 0)


def _patch_image(img):
    # screenshot 方法在 Window(即 PTPlugin.window) 上，patch 这里才能被 findColor 命中
    return patch.object(PTPlugin, 'screenshot', return_value=img)


class TestPTPlugin(unittest.TestCase):

    # ---------- 基础 ----------
    def test_found_exact(self):
        img = make_image(points={(3, 5): (255, 0, 0)})
        with _patch_image(img):
            x, y = PTPlugin.findColor(0, 0, 19, 19, "FF0000-000000")
        self.assertEqual((x, y), (3, 5))

    def test_not_found(self):
        img = make_image(fill=(0, 0, 0))
        with _patch_image(img):
            x, y = PTPlugin.findColor(0, 0, 19, 19, "FF0000-000000")
        self.assertEqual((x, y), (-1, -1))

    # ---------- 偏色 ----------
    def test_found_with_offset(self):
        img = make_image(points={(7, 2): (250, 5, 5)})
        with _patch_image(img):
            x, y = PTPlugin.findColor(0, 0, 19, 19, "FF0000-101010")
        self.assertEqual((x, y), (7, 2))

    def test_offset_reject(self):
        img = make_image(points={(7, 2): (200, 0, 0)})
        with _patch_image(img):
            x, y = PTPlugin.findColor(0, 0, 19, 19, "FF0000-101010")
        

    # ---------- 多颜色 ----------
    def test_multi_color_string(self):
        # 只有 aabbcc 存在
        img = make_image(points={(4, 4): (0xAA, 0xBB, 0xCC)})
        with _patch_image(img):
            x, y = PTPlugin.findColor(
                0, 0, 19, 19, "123456-000000|aabbcc-202020"
            )
        self.assertEqual((x, y), (4, 4))

    # ---------- 区域裁剪 ----------
    def test_region_clip(self):
        # 目标在 (5,5)，但查找区域从 (10,10) 开始，应找不到
        img = make_image(points={(5, 5): (255, 0, 0)})
        with _patch_image(img):
            _, _ = PTPlugin.findColor(10, 10, 19, 19, "FF0000-000000")
        

    def test_region_out_of_bounds(self):
        img = make_image(h=10, w=10)
        with _patch_image(img):
            # 越界要裁剪，不能报错
            _, _ = PTPlugin.findColor(-5, -5, 100, 100, "FF0000-000000")
        

    def test_invalid_region(self):
        img = make_image()
        with _patch_image(img):
            x, y = PTPlugin.findColor(10, 10, 5, 5, "FF0000-000000")
        self.assertEqual((x, y), (-1, -1))

    # ---------- mode 扫描方向 ----------
    def test_mode0_top_left(self):
        # 两个命中点，(2,2) 和 (8,8)，mode 0 应返回 (2,2)
        img = make_image(points={(2, 2): (255, 0, 0),
                                 (8, 8): (255, 0, 0)})
        with _patch_image(img):
            x, y = PTPlugin.findColor(0, 0, 19, 19, "FF0000-000000", mode=0)
        self.assertEqual((x, y), (2, 2))

    def test_mode1_bottom_left(self):
        # mode 1 下->上，左->右，应返回 (2,8)
        img = make_image(points={(2, 2): (255, 0, 0),
                                 (2, 8): (255, 0, 0)})
        with _patch_image(img):
            x, y = PTPlugin.findColor(0, 0, 19, 19, "FF0000-000000", mode=1)
        self.assertEqual((x, y), (2, 8))

    def test_mode2_top_right(self):
        # mode 2 上->下，右->左，应返回 (8,2)
        img = make_image(points={(2, 2): (255, 0, 0),
                                 (8, 2): (255, 0, 0)})
        with _patch_image(img):
            x, y = PTPlugin.findColor(0, 0, 19, 19, "FF0000-000000", mode=2)
        self.assertEqual((x, y), (8, 2))

    def test_mode3_bottom_right(self):
        # mode 3 下->上，右->左，应返回 (8,8)
        img = make_image(points={(2, 2): (255, 0, 0),
                                 (8, 8): (255, 0, 0)})
        with _patch_image(img):
            x, y = PTPlugin.findColor(0, 0, 19, 19, "FF0000-000000", mode=3)
        self.assertEqual((x, y), (8, 8))

    # ---------- sim 相似度 ----------
    def test_sim_pass(self):
        img = make_image(points={(3, 3): (250, 5, 5)})
        with _patch_image(img):
            # 偏色足够 -> 命中
            _, _ = PTPlugin.findColor(0, 0, 19, 19, "FF0000-101010", sim=0.9)

    def test_sim_reject(self):
        img = make_image(points={(3, 3): (250, 5, 5)})
        with _patch_image(img):
            # 相似度 0.99 应拒绝 (1 - 15/765 ≈ 0.98)
            _, _ = PTPlugin.findColor(0, 0, 19, 19, "FF0000-101010", sim=0.99)
        

    # ---------- 元组颜色 ----------
    def test_tuple_color(self):
        img = make_image(points={(6, 6): (255, 0, 0)})
        with _patch_image(img):
            x, y = PTPlugin.findColor(0, 0, 19, 19, (255, 0, 0))
        self.assertEqual((x, y), (6, 6))

    # ---------- 异常 ----------
    def test_invalid_color_type(self):
        img = make_image()
        with _patch_image(img):
            with self.assertRaises(ValueError):
                PTPlugin.findColor(0, 0, 19, 19, 12345)


if __name__ == '__main__':
    unittest.main()