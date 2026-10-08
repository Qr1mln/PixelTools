import cv2
import numpy as np


def _to_uint8(arr: np.ndarray) -> np.ndarray:
    """把任意深度的数组安全转成 uint8（0-255）。

    - uint8 原样返回；
    - 浮点且最大值 <= 1.0 视为 0-1 归一化，乘 255；
    - 其余按 0-255 裁剪。
    避免 cvtColor 因 CV_64F 等深度报 "Unsupported depth of input image"。
    """
    arr = np.asarray(arr)
    if arr.dtype == np.uint8:
        return arr
    f = arr.astype(np.float64)
    if f.size and f.max() <= 1.0:
        f = f * 255.0
    return np.clip(f, 0, 255).astype(np.uint8)


class Debug:
    """截图可视化调试工具类。

    用 cv2.imshow 展示 RGB 截图，并可在图上标记命中点 (x, y)。
    作为 mixin 挂到 Plugin 上，也可独立调用 Debug().preview(...) / Debug().show(...)。
    """
    @staticmethod
    def preview(img_rgb: np.ndarray,
                title: str = "PixelTools",
                x: int | list | tuple | None = None,
                y: int | list | tuple | None = None,
                points: list[tuple] | None = None,
                wait: int = 0,
                color: tuple[int, int, int] = (0, 0, 255)) -> None:
        """显示 RGB 截图，可选在若干 (x, y) 处画十字+圆圈标记。

        参数:
            img_rgb: (H, W, 3) RGB 数组（来自 screenshot）。任意深度均会归一化为 uint8。
            title:   窗口标题。
            x, y:    图中像素坐标（列, 行）。为 None 则不画标记。
                    支持单点：x=10, y=20；
                    也支持点列表：x=[10, 30], y=[20, 40]（二者长度需一致）。
            points:  (x, y) 元组列表，例如 [(107, 59), (120, 80)]；与 x/y 可同时用。
            wait:    0 表示等待任意按键后关闭；>0 为等待毫秒数。
            color:   标记颜色，cv2 的 BGR 顺序元组，默认 (0,0,255)=红。
        """
        img = _to_uint8(img_rgb)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        pts = list(Debug._normalize_points(x, y))
        if points:
            pts.extend((int(px), int(py)) for px, py in points)
        for px, py in pts:
            h, w = img.shape[:2]
            if 0 <= int(px) < w and 0 <= int(py) < h:
                cv2.drawMarker(img, (int(px), int(py)), color,
                               cv2.MARKER_CROSS, 20, 2)
                cv2.circle(img, (int(px), int(py)), 8, color, 2)
            else:
                print(f"标记点 ({px}, {py}) 超出图像范围 {w}x{h}，未绘制")
        cv2.imshow(title, img)
        cv2.waitKey(wait)
        cv2.destroyWindow(title)

    @staticmethod
    def _normalize_points(x, y):
        """把 x, y 归一化为 [(x0,y0), ...] 的点列表；任一为 None 返回空列表。"""
        if x is None or y is None:
            return []
        if isinstance(x, (list, tuple)) and isinstance(y, (list, tuple)):
            if len(x) != len(y):
                raise ValueError("x 与 y 列表长度不一致")
            return list(zip(x, y))
        return [(x, y)]
