"""
颜色模块 (Color) —— 大漠 API 模拟桩。

涵盖: 取色比色 / 找色 / 多点找色 / 颜色统计 / 平均色。

参数约定:
    - (x1,y1,x2,y2): 矩形区域左上角与右下角 (闭区间)。
    - color: 十六进制颜色字符串, 默认格式 "RRGGBB"。
    - sim:   相似度 0.0~1.0, 越大越严格。
    - dir:   查找方向 0~8 (语义见 _color_scan_order)。
"""

from __future__ import annotations

from typing import Any

from .base import display_backend


class Shot:
    """
    截图结果的最小统一接口, 与 mss 的 shot 同形 (duck typing)。

    图色代码只依赖 .rgb / .width / .height 三个成员, 因此窗口后台后端只要产出
    同形状的对象, 就能复用整屏后端的全部下游逻辑。
    """

    __slots__ = ("rgb", "width", "height")

    def __init__(self, rgb: bytes, width: int, height: int) -> None:
        self.rgb = rgb  # top-down 紧密打包的 RGB 字节
        self.width = width
        self.height = height


def client_rect_to_frame(
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    *,
    client_origin: tuple[int, int],
    window_origin: tuple[int, int],
    scale: float,
    frame_size: tuple[int, int],
) -> tuple[int, int, int, int] | None:
    """
    客户区逻辑闭区间 (x1, y1, x2, y2) -> WGC 帧内 **半开** 矩形, 并裁剪到帧边界。

    换算链: 客户区逻辑 -> 屏幕设备像素 -> 帧内像素
        帧内 = 客户区物理原点 + 逻辑 * scale - 窗口可视边框原点
    :param client_origin: 客户区左上角 (设备像素)。
    :param window_origin: 窗口可视边框左上角 (设备像素, 来自 dwm_frame_origin)。
    :param scale:         DPI 缩放比 (设备像素 / 逻辑坐标)。
    :param frame_size:    当前帧尺寸 (width, height), 用于裁剪。
    :return: (fx1, fy1, fx2, fy2) 半开区间; 与帧无交集返回 None。
    """
    ox, oy = client_origin
    wx, wy = window_origin
    fw, fh = frame_size
    # x2/y2 是闭区间, 故 +1 再取整, 得到半开末端
    fx1 = round(ox + x1 * scale) - wx
    fy1 = round(oy + y1 * scale) - wy
    fx2 = round(ox + (x2 + 1) * scale) - wx
    fy2 = round(oy + (y2 + 1) * scale) - wy
    fx1 = max(fx1, 0)
    fy1 = max(fy1, 0)
    fx2 = min(fx2, fw)
    fy2 = min(fy2, fh)
    if fx2 <= fx1 or fy2 <= fy1:
        return None
    return fx1, fy1, fx2, fy2


class ColorModule:
    """颜色相关方法 (大漠 API 模拟桩)。"""

    def get_color(self, x: int, y: int) -> str:
        """获取指定坐标的颜色, 返回 "RRGGBB" 格式字符串。"""
        ...

    def get_color_b_g_r(self, x: int, y: int) -> str:
        """获取指定坐标颜色 (BGR 顺序), 返回 "BBGGRR"。"""
        ...

    def get_color_h_s_v(self, x: int, y: int) -> str:
        """获取指定坐标颜色的 HSV 值, 返回 "h|s|v"。"""
        ...

    def get_pixel_color(self, x: int, y: int, mode: int = 0) -> str:
        """
        获取指定坐标的像素颜色。
        :param mode: 0=正常, 1=快速 (可能不精确)。
        """
        ...

    def cmp_color(self, x: int, y: int, color: str, sim: float) -> int:
        """
        比较指定坐标的颜色是否与目标颜色相似。
        :param color: 目标颜色 "RRGGBB"。
        :param sim:   相似度 0.0~1.0。
        :return: 1 相似, 0 不相似。
        """
        ...

    def get_color_num(
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

    def get_color_count(self, *args: Any) -> int:
        """get_color_num 的别名/扩展, 统计相似颜色出现次数。"""
        ...

    def get_ave_r_g_b(self, x1: int, y1: int, x2: int, y2: int) -> str:
        """获取指定区域的平均 RGB 颜色, 返回 "RRGGBB"。"""
        ...

    def get_ave_h_s_v(self, x1: int, y1: int, x2: int, y2: int) -> str:
        """获取指定区域的平均 HSV, 返回 "h|s|v"。"""
        ...

    def find_color(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
        dir_: int = 0,
    ) -> tuple[bool, int, int]:
        """
        在区域内查找指定颜色。
        :return: (是否找到, x, y); 命中返回 (True, x, y), 未找到/出错返回 (False, -1, -1)。
                 坐标基于绑定窗口客户区左上角 (若已 bind), 否则为屏幕坐标。
        使用现成的 mss 截图 + 像素扫描, 不自己写图色基础代码。
        :param color: 目标颜色, 支持大漠格式 "RRGGBB-DRDGDB"(各通道偏差) 与
                      多色 "|" 分隔, 如 "123456-000000|aabbcc-030303"。
        :param sim:   相似度 0.1~1.0, 越大越严格; 颜色串未带 -偏差时作回退容差。
        :param dir_:  大漠查找方向 0~8 (见 _color_scan_order)。
        """
        pts = self._find_color_points(x1, y1, x2, y2, color, sim, dir_)
        if pts:
            fx, fy = pts[0]
            return (True, fx, fy)
        return (False, -1, -1)

    def _grab_region(
        self, x1: int, y1: int, x2: int, y2: int
    ) -> tuple[Any, int, int, float, int, int] | None:
        """
        抓取区域截图: 输入坐标换算为设备像素后截图, 并裁剪到主显示器 / 窗口边界。
        后端由 bind 的 display 参数决定 (见 BaseModule.bind / display_backend),
        因此下游 (找色 / 预览) 无需区分。

        坐标换算 (ox,oy 为 bind 记录的客户区原点, **设备像素**, 见 api/dpi.py):
            设备 = 物理原点 + 逻辑坐标 * scale
            逻辑 = (设备 - 物理原点) / scale
        :return: (shot, gx1, gy1, scale, ox, oy); 区域无效/截图失败返回 None。
                 截图内像素 (px,py) 还原为输入坐标: round(((gx1 + px) - ox) / scale)。
        """
        backend = display_backend(getattr(self, "_display", ""))
        if backend == "window":
            return self._grab_region_window(x1, y1, x2, y2)
        if backend == "none":
            return None

        import mss

        ox, oy = getattr(self, "_client_origin", (0, 0))
        scale = self._dpi_scale()
        try:
            with mss.MSS() as sct:
                mon = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                m_left, m_top = mon["left"], mon["top"]
                m_right = m_left + mon["width"] - 1
                m_bottom = m_top + mon["height"] - 1
                gx1 = max(round(ox + x1 * scale), m_left)
                gy1 = max(round(oy + y1 * scale), m_top)
                gx2 = min(round(ox + x2 * scale), m_right)
                gy2 = min(round(oy + y2 * scale), m_bottom)
                if gx2 < gx1 or gy2 < gy1:
                    return None
                shot = sct.grab(
                    {
                        "left": gx1,
                        "top": gy1,
                        "width": gx2 - gx1 + 1,
                        "height": gy2 - gy1 + 1,
                    }
                )
                return shot, gx1, gy1, scale, ox, oy
        except Exception:
            return None

    def _grab_region_window(
        self, x1: int, y1: int, x2: int, y2: int
    ) -> tuple[Any, int, int, float, int, int] | None:
        """
        从窗口后台捕获会话 (WGC) 取区域: 客户区逻辑坐标 -> 帧内像素 -> RGB 字节。

        与整屏后端的唯一区别是画面来源, 返回结构完全一致:
        gx1/gy1 仍为该区域左上角的 **屏幕设备像素**, 以保证下游的
        "输入坐标 = round(((gx1 + px) - ox) / scale)" 反算公式不变。
        """
        import numpy as np

        capture = getattr(self, "_capture", None)
        if capture is None:
            return None
        frame = capture.grab()
        if frame is None:
            return None

        fh, fw = int(frame.shape[0]), int(frame.shape[1])
        rect = client_rect_to_frame(
            x1,
            y1,
            x2,
            y2,
            client_origin=getattr(self, "_client_origin", (0, 0)),
            window_origin=getattr(self, "_window_origin", (0, 0)),
            scale=self._dpi_scale(),
            frame_size=(fw, fh),
        )
        if rect is None:
            return None
        fx1, fy1, fx2, fy2 = rect

        # WGC 帧是 BGRA; 转成 RGB 且 ascontiguousarray 保证字节紧凑 (下游按字节索引)
        bgra = np.ascontiguousarray(frame[fy1:fy2, fx1:fx2, 2::-1])
        rgb = bgra.tobytes()
        ox, oy = getattr(self, "_client_origin", (0, 0))
        wx, wy = getattr(self, "_window_origin", (0, 0))
        return (
            Shot(rgb, int(bgra.shape[1]), int(bgra.shape[0])),
            wx + fx1,
            wy + fy1,
            self._dpi_scale(),
            ox,
            oy,
        )

    def _find_color_points(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
        dir_: int = 0,
    ) -> list[tuple[int, int]]:
        """返回区域内所有匹配 color 的坐标列表 (输入坐标系); 失败/无匹配返回 []。"""
        # 1) 规范化区域为左上-右下
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        w = x2 - x1 + 1
        h = y2 - y1 + 1
        if w <= 0 or h <= 0:
            return []

        # 2) 解析目标颜色: 支持大漠 "RRGGBB-DRDGDB" 与多色 "|" 分隔
        targets = self._parse_dm_colors(color, sim)
        if not targets:
            return []

        # 3) 抓取区域截图 (内含客户区偏移 + 高 DPI 换算 + 裁剪)
        grabbed = self._grab_region(x1, y1, x2, y2)
        if grabbed is None:
            return []
        shot, gx1, gy1, scale, ox, oy = grabbed

        # 4) 按大漠 dir 扫描顺序收集所有匹配点, 命中点还原为输入坐标系
        try:
            rgb = shot.rgb  # mss: top-down 紧密打包的 RGB 字节
            w, h = shot.width, shot.height
            # 高 DPI 下多个设备像素可能映射到同一逻辑坐标, 故按逻辑坐标去重
            seen: set[tuple[int, int]] = set()
            points: list[tuple[int, int]] = []
            for px, py in self._color_scan_order(w, h, dir_):
                i = (py * w + px) * 3
                pr, pg, pb = rgb[i], rgb[i + 1], rgb[i + 2]
                for (tr, tg, tb, trr, trg, trb) in targets:
                    if (
                        abs(pr - tr) <= trr
                        and abs(pg - tg) <= trg
                        and abs(pb - tb) <= trb
                    ):
                        lx = round(((gx1 + px) - ox) / scale)
                        ly = round(((gy1 + py) - oy) / scale)
                        p = (lx, ly)
                        if p not in seen:
                            seen.add(p)
                            points.append(p)
                        break
            return points
        except Exception:
            return []

    @staticmethod
    def _dpi_scale() -> float:
        """
        返回 "截图设备像素 / 逻辑坐标" 的缩放比 (如 150% 缩放 -> 1.5)。

        实现委托给 api/dpi.py 的 dpi_scale(): 先幂等锁定进程 DPI 感知, 再取
        GetDpiForSystem()/96, 保证与调用顺序无关 (详见该模块说明)。
        """
        from .dpi import dpi_scale

        return dpi_scale()

    @staticmethod
    def _color_scan_order(w: int, h: int, dir_: int) -> list[tuple[int, int]]:
        """
        按大漠 dir 方向生成扫描顺序 (0~8)。约定: 描述中第一个方向为"快轴"(内层),
        第二个方向为"慢轴"(外层)。
          0: 左→右, 上→下    1: 左→右, 下→上
          2: 右→左, 上→下    3: 右→左, 下→上
          4: 从中心向外       5: 上→下, 左→右
          6: 上→下, 右→左    7: 下→上, 左→右
          8: 下→上, 右→左
        """
        xs = range(w)
        xs_r = range(w - 1, -1, -1)
        ys = range(h)
        ys_r = range(h - 1, -1, -1)
        if dir_ == 0:
            return [(x, y) for y in ys for x in xs]
        if dir_ == 1:
            return [(x, y) for y in ys_r for x in xs]
        if dir_ == 2:
            return [(x, y) for y in ys for x in xs_r]
        if dir_ == 3:
            return [(x, y) for y in ys_r for x in xs_r]
        if dir_ == 4:  # 中心向四周
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            pts = [(x, y) for y in range(h) for x in range(w)]
            pts.sort(key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
            return pts
        if dir_ == 5:
            return [(x, y) for x in xs for y in ys]
        if dir_ == 6:
            return [(x, y) for x in xs_r for y in ys]
        if dir_ == 7:
            return [(x, y) for x in xs for y in ys_r]
        if dir_ == 8:
            return [(x, y) for x in xs_r for y in ys_r]
        # 非法 dir 回退到 dir 0
        return [(x, y) for y in ys for x in xs]

    @staticmethod
    def _parse_dm_colors(
        color: str, sim: float
    ) -> list[tuple[int, int, int, int, int, int]]:
        """
        解析大漠颜色串为匹配目标列表, 每项 (r, g, b, tol_r, tol_g, tol_b)。
        - 多色以 "|" 分隔, 如 "123456|aabbcc-030303"。
        - 单色支持 "RRGGBB-DRDGDB", DRDGDB 为各通道允许偏差(十六进制);
          未给出 -偏差时回退为 sim 推导的容差 int((1-sim)*255)。
        - 反色 "@..." (大漠付费功能) 暂不支持, 视为非法跳过。
        """
        default_tol = int((1.0 - max(0.0, min(1.0, sim))) * 255)
        targets: list[tuple[int, int, int, int, int, int]] = []
        for part in color.split("|"):
            part = part.strip()
            if not part or part.startswith("@"):
                continue
            base = part
            tol = (default_tol, default_tol, default_tol)
            if "-" in part:
                base, delta = part.split("-", 1)
                try:
                    tol = (
                        int(delta[0:2], 16),
                        int(delta[2:4], 16),
                        int(delta[4:6], 16),
                    )
                except (ValueError, IndexError):
                    tol = (default_tol, default_tol, default_tol)
            try:
                targets.append(
                    (
                        int(base[0:2], 16),
                        int(base[2:4], 16),
                        int(base[4:6], 16),
                        tol[0],
                        tol[1],
                        tol[2],
                    )
                )
            except (ValueError, IndexError):
                continue
        return targets

    def find_color_ex(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
        dir_: int = 0,
    ) -> list[tuple[int, int]]:
        """查找区域内所有匹配颜色, 返回坐标列表 [(x, y), ...]; 无匹配返回 []。"""
        return self._find_color_points(x1, y1, x2, y2, color, sim, dir_)

    def find_color_e(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        color: str,
        sim: float,
        dir_: int = 0,
    ) -> str:
        """大漠 FindColorE: 命中返回 "x|y", 未找到返回 ""。"""
        found, fx, fy = self.find_color(x1, y1, x2, y2, color, sim, dir_)
        return f"{fx}|{fy}" if found else ""

    def find_color_block(
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

    def find_multi_color(
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
        :param color:        附加的偏移颜色串 (可空), 同 offset_color 格式。
        :return: 首个命中的锚点 "x|y", 未找到/出错返回 ""。
        """
        pts = self._find_multi_color_points(
            x1, y1, x2, y2, first_color, offset_color, sim, dir_, color
        )
        if pts:
            fx, fy = pts[0]
            return f"{fx}|{fy}"
        return ""

    def find_multi_color_ex(
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
        """find_multi_color 的全区域版本, 返回所有匹配锚点 "x1|y1|x2|y2|..."; 无匹配返回 ""。"""
        pts = self._find_multi_color_points(
            x1, y1, x2, y2, first_color, offset_color, sim, dir_, color
        )
        return "|".join(f"{x}|{y}" for x, y in pts)

    def _find_multi_color_points(
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
    ) -> list[tuple[int, int]]:
        """返回所有满足多点配色条件的锚点坐标列表 (first_color 命中位置); 失败/无匹配返回 []。"""
        # 1) 先找基准色候选锚点 (复用单点找色逻辑 + dir 扫描顺序)
        candidates = self._find_color_points(x1, y1, x2, y2, first_color, sim, dir_)
        if not candidates:
            return []

        # 2) 解析偏移串 (offset_color 与附加的 color 串格式相同)
        offsets = self._parse_offset_colors(offset_color)
        offsets += self._parse_offset_colors(color)
        if not offsets:
            return candidates  # 无偏移定义时退化为单点找色

        # 3) 对每个锚点校验各偏移处颜色
        tol = int((1.0 - sim) * 255)
        ox, oy = getattr(self, "_client_origin", (0, 0))
        scale = self._dpi_scale()
        results: list[tuple[int, int]] = []
        for cx, cy in candidates:
            ok = True
            for dx, dy, oc in offsets:
                tgt = self._parse_color(oc)
                if tgt is None:
                    ok = False
                    break
                # 客户区(逻辑) -> 设备像素: 原点已是设备像素, 客户区坐标乘 scale
                sx = round(ox + (cx + dx) * scale)
                sy = round(oy + (cy + dy) * scale)
                rgb = self._get_pixel_rgb(sx, sy)
                if rgb is None or not self._color_in_tol(*rgb, *tgt, tol):
                    ok = False
                    break
            if ok:
                results.append((cx, cy))
        return results

    @staticmethod
    def _parse_offset_colors(s: str) -> list[tuple[int, int, str]]:
        """解析 "dx|dy|RRGGBB,dx2|dy2|RRGGBB" 形式的偏移串。"""
        specs: list[tuple[int, int, str]] = []
        if not s:
            return specs
        for part in s.split(","):
            part = part.strip()
            if not part:
                continue
            bits = part.split("|")
            if len(bits) != 3:
                continue
            try:
                specs.append((int(bits[0]), int(bits[1]), bits[2]))
            except ValueError:
                continue
        return specs

    @staticmethod
    def _parse_color(color: str) -> tuple[int, int, int] | None:
        """解析 "RRGGBB" 为 (r, g, b); 格式非法返回 None。"""
        try:
            return (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _color_in_tol(
        pr: int, pg: int, pb: int, tr: int, tg: int, tb: int, tol: int
    ) -> bool:
        """判断像素 (pr,pg,pb) 与目标 (tr,tg,tb) 各通道差是否在 tol 内。"""
        return abs(pr - tr) <= tol and abs(pg - tg) <= tol and abs(pb - tb) <= tol

    def _get_pixel_rgb(self, sx: int, sy: int) -> tuple[int, int, int] | None:
        """取屏幕**设备像素**坐标 (sx, sy) 处单像素 RGB; 失败返回 None。"""
        # 窗口后台后端: 直接读 WGC 帧, 不经过屏幕 (窗口被遮挡/最小化时依然有效)
        if display_backend(getattr(self, "_display", "")) == "window":
            capture = getattr(self, "_capture", None)
            frame = capture.grab() if capture is not None else None
            if frame is None:
                return None
            wx, wy = getattr(self, "_window_origin", (0, 0))
            px, py = int(sx) - wx, int(sy) - wy
            if 0 <= py < int(frame.shape[0]) and 0 <= px < int(frame.shape[1]):
                b, g, r = (int(v) for v in frame[py, px, :3])
                return (r, g, b)
            return None

        import mss

        try:
            with mss.MSS() as sct:
                shot = sct.grab({"left": sx, "top": sy, "width": 1, "height": 1})
                rgb = shot.rgb
                return (rgb[0], rgb[1], rgb[2])
        except Exception:
            return None

    def retry_find_color(
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
