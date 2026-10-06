"""
找色结果可视化 (调试用)。

思路: 先用 find_color / find_color_ex 拿到结果, 再调用 show_found_points
重新截取该区域, 把命中点用 cv2 描绘出来并快速显示。

依赖现成包: mss (截图) + opencv-python / numpy (绘制与显示)。
"""

from __future__ import annotations

import cv2
import numpy as np


def show_found_points(
    pt,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    points: list[tuple[int, int]],
    marker: int = 9,
    bgr: tuple[int, int, int] = (255, 0, 255),
    max_window: int = 1600,
    wait: int = 0,
) -> None:
    """
    重新截取区域截图, 把上次找色的命中点描绘出来并用 cv2 显示。

    :param pt:         PtPlugin 实例 (复用其截图与 DPI 换算)。
    :param points:     上次找色得到的输入坐标系坐标 [(x, y), ...]。
    :param marker:     命中标记边长(像素), 建议奇数便于居中。
    :param bgr:        标记颜色, cv2 为 BGR 顺序; (255, 0, 255) 即粉色。
    :param max_window: 显示窗口最大宽度, 超出则等比缩小 (仅影响显示, 不影响绘制)。
    :param wait:       waitKey 毫秒数, 0=等待任意按键关闭。
    """
    grabbed = pt._grab_region(x1, y1, x2, y2)
    if grabbed is None:
        print("show_found_points: 无法截取区域", (x1, y1, x2, y2))
        return
    shot, gx1, gy1, scale, ox, oy = grabbed

    # mss 的 rgb 是只读字节, 需拷贝后才能在上面绘制
    img = np.frombuffer(shot.rgb, dtype=np.uint8).reshape(
        (shot.height, shot.width, 3)
    ).copy()
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # 输入(逻辑)坐标 -> 设备像素 -> 截图内相对坐标 (与 _grab_region 换算对称)
    half = marker // 2
    for lx, ly in points:
        cx = round(ox + lx * scale) - gx1
        cy = round(oy + ly * scale) - gy1
        cv2.rectangle(img, (cx - half, cy - half), (cx + half, cy + half), bgr, -1)

    h, w = img.shape[:2]
    if 0 < max_window < w:
        img = cv2.resize(img, (max_window, round(h * max_window / w)))
    cv2.imshow("find result", img)
    cv2.waitKey(wait)
    cv2.destroyAllWindows()
