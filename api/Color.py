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

def parse_single_color(s: str):
    """
    解析单个颜色 "RRGGBB-DRDGDB" -> ((r,g,b), (dr,dg,db))
    如果没有 '-'，则偏色默认为 (0,0,0)
    """
    s = s.strip()
    if '-' in s:
        main, bias = s.split('-', 1)
    else:
        main, bias = s, '000000'
    r  = int(main[0:2], 16); g  = int(main[2:4], 16); b  = int(main[4:6], 16)
    dr = int(bias[0:2], 16); dg = int(bias[2:4], 16); db = int(bias[4:6], 16)
    return (r, g, b), (dr, dg, db)

def parse_offset_colors(s: str):
    """
    解析偏移颜色组 "x1|y1|颜色1,x2|y2|颜色2,..."
    返回 [(dx, dy, (r,g,b), (dr,dg,db)), ...]
    """
    result = []
    for item in s.split(','):
        item = item.strip()
        if not item:
            continue
        parts = item.split('|')
        if len(parts) != 3:
            continue
        dx, dy = int(parts[0]), int(parts[1])
        rgb, bias = parse_single_color(parts[2])
        result.append((dx, dy, rgb, bias))
    return result

def check_offsets(img, cx, cy, offsets, sim) -> bool:
    """
    校验主点 (cx, cy) 处的所有偏移点是否匹配。
    全部通过返回 True，任一失败返回 False。
    """
    H, W = img.shape[:2]
    for dx, dy, (tr, tg, tb), (dr, dg, db) in offsets:
        px = cx + dx
        py = cy + dy
        if px < 0 or py < 0 or px >= W or py >= H:
            return False

        r = int(img[py, px, 0])
        g = int(img[py, px, 1])
        b = int(img[py, px, 2])

        diff = abs(r - tr) + abs(g - tg) + abs(b - tb)

        # 偏移点容差：偏色优先；偏色全 0 时用 sim 推导总差容差，
        # 否则偏色=0 会要求偏移点“逐像素完全一致”，sim 形同虚设。
        if dr == dg == db == 0 and sim is not None:
            if diff > int(round((1.0 - sim) * 765.0)):
                return False
        else:
            # 偏色判断
            if abs(r - tr) > dr or abs(g - tg) > dg or abs(b - tb) > db:
                return False
            # 相似度判断
            if sim is not None and (1.0 - diff / 765.0) < sim:
                return False

    return True


def _main_color_mask(r, g, b, mr, mg, mb, mdr, mdg, mdb, sim):
    """按主色生成候选掩码。

    偏色优先；若偏色全为 0 且给定了 sim，则用 sim 推导总差容差，
    否则偏色=0 会要求主色“逐像素完全一致”，导致 sim 形同虚设、
    真实截图里几乎只能命中一个像素级精确点。
    """
    if mdr == mdg == mdb == 0 and sim is not None:
        tol = int(round((1.0 - sim) * 765.0))   # 三通道总差容差
        return (np.abs(r - mr) + np.abs(g - mg) + np.abs(b - mb)) <= tol
    mask = (
        (np.abs(r - mr) <= mdr) &
        (np.abs(g - mg) <= mdg) &
        (np.abs(b - mb) <= mdb)
    )
    if sim is not None:
        diff_sum = np.abs(r - mr) + np.abs(g - mg) + np.abs(b - mb)
        mask &= (1.0 - diff_sum / 765.0) >= sim
    return mask


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
        img_rgb = PTPlugin.screenshot(x1, y1, x2, y2)  # (H, W, 3) RGB
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
    前提是：特征点要选得稳定、独特、高对比，偏色和相似度也要调得合理。
    
    FindMultiColor 是在动态画面中，用人工选定的“颜色点阵”作为相对不变的结构特征，来定位目标。
    """

    # ============================================================
    # 多点找色
    # ============================================================
    @staticmethod
    def findMultiColor(x1, y1, x2, y2,
                       first_color, offset_colors,
                       sim=0.9, mode=0):
        """
        函数简介:
            查找指定区域内的多点颜色。
            主点颜色 + 若干偏移点的颜色特征，全部满足才视为命中。

        参数:
            x1, y1, x2, y2 : 区域左上、右下坐标（客户区坐标）
            first_color    : 主点颜色，格式 "RRGGBB-DRDGDB" 或 (r,g,b)
            offset_colors  : 偏移颜色组，格式 "x1|y1|RRGGBB-DRDGDB,x2|y2|..."
            sim            : 相似度 0.1~1.0
            mode           : 查找方向
                             0: 从左到右,从上到下
                             1: 从左到右,从下到上
                             2: 从右到左,从上到下
                             3: 从右到左,从下到上
                             4: 从中心往外
                             5: 从上到下,从左到右
                             6: 从上到下,从右到左
                             7: 从下到上,从左到右
                             8: 从下到上,从右到左

        返回:
            (x, y) 命中坐标；未找到返回 (-1, -1)
        """
        # ---- 1. 归一化主色 ----
        if isinstance(first_color, str):
            first_str = first_color
        elif isinstance(first_color, (tuple, list)):
            first_str = '%02X%02X%02X-000000' % tuple(first_color)
        else:
            raise ValueError('first_color 格式错误')

        # ---- 2. 裁剪坐标 + 截图 ----
        x1 = max(0, x1); y1 = max(0, y1)
        x2 = max(x1, x2); y2 = max(y1, y2)
        from api import PTPlugin
        img = PTPlugin.screenshot(x1, y1, x2, y2)   # (H, W, 3) RGB
        H, W = img.shape[:2]
        if H == 0 or W == 0:
            return -1, -1

        # ---- 3. 解析颜色 ----
        (mr, mg, mb), (mdr, mdg, mdb) = parse_single_color(first_str)
        offsets = parse_offset_colors(offset_colors)

        # ---- 4. 主点掩码（向量化）----
        r = img[:, :, 0].astype(np.int16)
        g = img[:, :, 1].astype(np.int16)
        b = img[:, :, 2].astype(np.int16)

        main_mask = _main_color_mask(r, g, b, mr, mg, mb, mdr, mdg, mdb, sim)

        if not main_mask.any():
            return -1, -1

        # ---- 5. 按 mode 排序候选主点 ----
        ys, xs = np.where(main_mask)
        h, w = main_mask.shape

        if mode == 0:
            order = np.lexsort((xs, ys))
        elif mode == 1:
            order = np.lexsort((xs, -ys))
        elif mode == 2:
            order = np.lexsort((-xs, ys))
        elif mode == 3:
            order = np.lexsort((-xs, -ys))
        elif mode == 4:
            cx, cy = w / 2.0, h / 2.0
            order = np.argsort((xs - cx) ** 2 + (ys - cy) ** 2)
        elif mode == 5:
            order = np.lexsort((ys, xs))
        elif mode == 6:
            order = np.lexsort((ys, -xs))
        elif mode == 7:
            order = np.lexsort((-ys, xs))
        else:  # 8
            order = np.lexsort((-ys, -xs))

        xs = xs[order]; ys = ys[order]

        # ---- 6. 逐个候选点校验偏移组 ----
        for cx, cy in zip(xs.tolist(), ys.tolist()):
            if check_offsets(img, cx, cy, offsets, sim):
                return int(cx), int(cy)

        return -1, -1




    # ============================================================
    # 多点找色（返回所有命中点）
    # ============================================================
    @staticmethod
    def findMultiColorEx( x1, y1, x2, y2,
                         first_color, offset_colors,
                         sim=0.9, max_count=1800):
        """
        找出区域内所有满足多点颜色特征的坐标。
        返回 [(x, y), ...]，最多 max_count 个。
        """
        if isinstance(first_color, str):
            first_str = first_color
        elif isinstance(first_color, (tuple, list)):
            first_str = '%02X%02X%02X-000000' % tuple(first_color)
        else:
            raise ValueError('first_color 格式错误')

        x1 = max(0, x1); y1 = max(0, y1)
        x2 = max(x1, x2); y2 = max(y1, y2)
        from api import PTPlugin
        img = PTPlugin.screenshot(x1, y1, x2, y2)
        H, W = img.shape[:2]
        if H == 0 or W == 0:
            return []

        (mr, mg, mb), (mdr, mdg, mdb) = parse_single_color(first_str)
        offsets = parse_offset_colors(offset_colors)

        r = img[:, :, 0].astype(np.int16)
        g = img[:, :, 1].astype(np.int16)
        b = img[:, :, 2].astype(np.int16)

        main_mask = _main_color_mask(r, g, b, mr, mg, mb, mdr, mdg, mdb, sim)

        if not main_mask.any():
            return []

        ys, xs = np.where(main_mask)
        n_candidates = len(xs)
        results = []
        n_passed = 0
        for cx, cy in zip(xs.tolist(), ys.tolist()):
            if check_offsets(img, cx, cy, offsets, sim):
                results.append((int(cx), int(cy)))
                n_passed += 1
                if len(results) >= max_count:
                    break
        # ---- DEBUG ----
        print(f"[findMultiColorEx DEBUG] 区域=({x1},{y1},{x2},{y2}) "
              f"主色={first_str} sim={sim} "
              f"候选主色点数={n_candidates} 通过偏移校验点数={n_passed} "
              f"返回点数={len(results)}")
        # ---------------
        return results