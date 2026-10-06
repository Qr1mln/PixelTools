import ctypes
import logging

import win32gui

# DPI 感知级别 (PROCESS_DPI_AWARENESS)
PROCESS_DPI_UNAWARE = 0
PROCESS_SYSTEM_DPI_AWARE = 1
PROCESS_PER_MONITOR_DPI_AWARE = 2
# PROCESS_PER_MONITOR_DPI_AWARE_V2 = PROCESS_PER_MONITOR_DPI_AWARE + 1
PROCESS_PER_MONITOR_DPI_AWARE_V2 = 3

# DWM 扩展边框属性：返回窗口真实物理矩形（不含阴影/边框留白）
_DWMWA_EXTENDED_FRAME_BOUNDS = 9


def set_dpi_aware(awareness: int = PROCESS_PER_MONITOR_DPI_AWARE_V2) -> bool:
    """让当前进程感知 DPI，使 GetWindowRect / mss / ClientToScreen 的坐标统一为物理像素。

    必须在任何窗口/截图操作之前调用一次。重复调用安全。
    开启后，ClientToScreen 会直接把“窗口客户区逻辑坐标”映射到“物理屏幕坐标”，
    无需再手动做 DPI 缩放修正。返回是否成功（失败不致命，坐标可能不准）。
    """
    try:
        # Win8.1+ : shcore.SetProcessDpiAwareness
        ctypes.windll.shcore.SetProcessDpiAwareness(awareness)
        return True
    except Exception:
        pass
    try:
        # 旧系统 / 已被设置时的回退
        ctypes.windll.user32.SetProcessDPIAware()
        return True
    except Exception as e:
        logging.warning(f"设置 DPI 感知失败: {e}")
        return False


def get_window_rect_physical(hwnd: int) -> tuple[int, int, int, int]:
    """返回窗口真实物理像素矩形 (left, top, right, bottom)。

    优先用 DWM 扩展边框；失败回退到 GetWindowRect。
    调用前应已 set_dpi_aware，否则返回 DPI 虚拟化后的逻辑坐标。
    """
    rect = ctypes.wintypes.RECT()
    try:
        ctypes.windll.dwmapi.DwmGetWindowAttribute(
            hwnd,
            _DWMWA_EXTENDED_FRAME_BOUNDS,
            ctypes.byref(rect),
            ctypes.sizeof(rect),
        )
        return rect.left, rect.top, rect.right, rect.bottom
    except Exception:
        # 回退：win32gui.GetWindowRect 返回 (left, top, right, bottom)
        return win32gui.GetWindowRect(hwnd)


def get_client_origin_physical(hwnd: int) -> tuple[int, int]:
    """返回客户区左上角在屏幕上的物理像素坐标 (x, y)。

    进程已 DPI 感知时，ClientToScreen 直接返回物理坐标；同时窗口客户区坐标
    也已映射到物理像素，因此截图时直接用 ClientToScreen(hwnd, (x, y)) 即可。
    """
    try:
        return win32gui.ClientToScreen(hwnd, (0, 0))
    except Exception:
        left, top, _, _ = get_window_rect_physical(hwnd)
        return left, top
