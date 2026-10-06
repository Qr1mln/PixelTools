"""
DPI 相关工具 (Windows) —— 供 base(窗口绑定) 与 color(截图) 共用。

背景 (实测): mss 在构造 mss.MSS() 时会把进程切成 DPI-aware, 导致同一进程内
先后取得的窗口坐标 / 屏幕尺寸不在同一空间:
    - 感知前 (unaware): 坐标被 Windows 虚拟化 -> 逻辑坐标 (如宽 2560)
    - 感知后 (aware):   返回真实设备像素         (如宽 3840)
若不统一, 同一进程内的语义就会漂移: bind 取到的原点可能是逻辑值, 而稍后的
截图换算又按另一种理解处理 -> 区域双重缩放 / 错位。

解决: 在任何取坐标的动作之前先幂等地锁定感知状态, 之后一律以 **设备像素** 为
唯一标准, 换算公式统一为:
    设备 = 物理原点 + 逻辑坐标 * scale
    逻辑 = (设备 - 物理原点) / scale
"""

from __future__ import annotations


def ensure_dpi_aware() -> None:
    """把进程置为 per-monitor DPI aware (幂等; 失败或已设置均忽略)。"""
    try:
        import ctypes

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PER_MONITOR_AWARE
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def dpi_scale() -> float:
    """
    返回 "设备像素 / 逻辑坐标" 的缩放比 (如 150% 缩放 -> 1.5)。

    先锁定感知状态, 保证与调用顺序无关; 取不到时回退 1.0。
    """
    ensure_dpi_aware()
    try:
        import ctypes

        scale = ctypes.windll.user32.GetDpiForSystem() / 96.0
        return scale if scale > 0 else 1.0
    except Exception:
        return 1.0
