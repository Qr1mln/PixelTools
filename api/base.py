"""基础 / 窗口绑定模块 —— 使用图色与键鼠前通常需要先绑定窗口。"""

from __future__ import annotations

import threading
import time
from typing import Any

from .dpi import ensure_dpi_aware


# display 取值 -> 捕获后端。取值依据大漠 BindWindow 文档。
# 注意: 空串 (未绑定时的默认值) 归入整屏, 以保持"未绑定也能抓屏"的旧行为。
_WINDOW_MODES = frozenset({"dx", "dx2", "dx2.0", "dx3", "dx.graphic.2d", "dx.graphic.3d"})
_NONE_MODES = frozenset({"none", "null"})


def display_backend(display: str) -> str:
    """
    把 bind 的 display 字符串映射为捕获后端。

    :param display: 大漠图色属性, 如 "normal" / "gdi" / "dx" / "none"。
    :return: "screen" (整屏) / "window" (窗口后台) / "none" (不绑定图色);
             未知取值一律退回 "screen", 保证 bind 不因写法差异直接失败。
    """
    d = (display or "").strip().lower()
    if d in _WINDOW_MODES:
        return "window"
    if d in _NONE_MODES:
        return "none"
    return "screen"


def dwm_frame_origin(hwnd: int) -> tuple[int, int] | None:
    """
    取窗口 **可视边框** 左上角 (DWM 扩展边框, 设备像素) —— WGC 帧对齐基准。

    :return: (x, y); 取不到 (无 DWM / 窗口已销毁) 返回 None, 由调用方退回 GetWindowRect。
    """
    try:
        import ctypes
        from ctypes import wintypes

        class RECT(ctypes.Structure):
            _fields_ = [
                ("left", wintypes.LONG),
                ("top", wintypes.LONG),
                ("right", wintypes.LONG),
                ("bottom", wintypes.LONG),
            ]

        rect = RECT()
        # DWMWA_EXTENDED_FRAME_BOUNDS = 9
        hr = ctypes.windll.dwmapi.DwmGetWindowAttribute(
            wintypes.HWND(hwnd),  # type: ignore[arg-type]
            ctypes.c_uint(9),
            ctypes.byref(rect),
            ctypes.sizeof(rect),
        )
        if hr != 0:
            return None
        return (int(rect.left), int(rect.top))
    except Exception:
        return None


class WindowCapture:
    """
    窗口后台捕获会话 (Windows Graphics Capture API, 由 windows-capture 包提供)。

    行为:
        - 只在 bind 到 dx 类 display 时创建, 避免无谓的线程开销。
        - 只保留 **最新一帧** (WGC 仅在窗口内容变化时推帧, 静止窗口不产生拷贝)。
        - 帧数据在回调里必须立刻复制: frame_buffer 是零拷贝视图, 回调结束即失效。
    """

    def __init__(self, hwnd: int) -> None:
        self._hwnd = hwnd
        self._control: Any = None
        self._frame: Any = None  # numpy.ndarray (h, w, 4) BGRA
        self._lock = threading.Lock()
        self._closed = False

    @property
    def hwnd(self) -> int:
        return self._hwnd

    def start(self, timeout: float = 3.0) -> bool:
        """
        建立捕获会话并等待首帧。

        :param timeout: 等待首帧的秒数 (WGC 建链较慢, 大漠文档也提示 dx 绑定耗时)。
        :return: 收到首帧 True; 超时 / 会话被关闭 / 建链失败 False。
        """
        from windows_capture import WindowsCapture as _WC

        self.stop()
        with self._lock:
            self._frame = None
            self._closed = False

        cap = _WC(cursor_capture=False, draw_border=None, window_hwnd=self._hwnd)
        # 注意: 不能用 @cap.event 装饰器 (它要求函数名必须是 on_frame_arrived /
        # on_closed), 这里直接赋值回调, 对函数名无约束。
        cap.frame_handler = self._on_frame_arrived
        cap.closed_handler = self._on_closed
        try:
            self._control = cap.start_free_threaded()
        except Exception:
            self._control = None
            return False

        deadline = time.monotonic() + max(0.0, timeout)
        while time.monotonic() < deadline:
            with self._lock:
                if self._frame is not None:
                    return True
                closed = self._closed
            if closed:
                return False
            time.sleep(0.005)
        with self._lock:
            return self._frame is not None

    def grab(self) -> Any:
        """返回最新一帧 (numpy (h, w, 4) BGRA); 尚无帧返回 None。"""
        with self._lock:
            return self._frame

    def stop(self) -> None:
        """停止捕获线程并释放会话 (可重复调用)。"""
        control, self._control = self._control, None
        if control is None:
            return
        try:
            control.stop()
        except Exception:
            pass
        try:
            control.wait()
        except Exception:
            pass

    def _on_frame_arrived(self, frame: Any, capture_control: Any) -> None:
        # frame_buffer 是映射内存的零拷贝视图, 只在本次回调期间有效 -> 必须立刻复制
        with self._lock:
            self._frame = frame.frame_buffer.copy()

    def _on_closed(self) -> None:
        self._closed = True


class BaseModule:
    """基础与窗口绑定相关方法 (大漠 API)。"""

    def __init__(self) -> None:
        # 尽早锁定 DPI 感知状态, 让后续所有窗口坐标都处于同一空间 (见 api/dpi.py)
        ensure_dpi_aware()
        # 绑定状态 (由 bind / bind_window 填充)
        self.hwnd: int = 0
        self._bound: bool = False
        self._client_origin: tuple[int, int] = (0, 0)
        self._client_size: tuple[int, int] = (0, 0)
        # 窗口可视边框左上角 (设备像素): 窗口后台捕获的帧对齐基准, 区别于 GetWindowRect
        self._window_origin: tuple[int, int] = (0, 0)
        self._display: str = ""
        self._mouse: str = ""
        self._keypad: str = ""
        self._mode: int = 0
        # 窗口后台捕获会话 (仅 display 为 dx 类时存在, 否则 None)
        self._capture: Any = None
        super().__init__()

    def ver(self) -> str:
        """获取当前大漠插件版本号, 例如 "3.1238"。"""
        return "1.0.0"

    def set_path(self, path: str) -> int:
        """
        设置大漠插件的全局路径 (字库、图片资源等所在目录)。
        :param path: 资源目录的绝对路径。
        :return: 1 成功, 0 失败。
        """
        ...

    def bind_window(
        self,
        hwnd: int,
        display: str,
        mouse: str,
        keypad: str,
        mode: int,
    ) -> bool:
        """
        绑定窗口, 使其接受大漠的图色/鼠标/键盘操作 (使用现成的 pywin32 校验窗口句柄)。

        display 决定图色来源后端 (见本模块顶部的 display_backend):
            "normal"/"gdi"/"gdi2" -> mss 整屏截图;
            "dx"/"dx2"/"dx3"      -> windows-capture 窗口后台捕获 (可取被遮挡/最小化窗口,
                                     支持 DX 窗口), 建链失败则绑定失败 (对齐大漠语义);
            "none"                -> 不绑定图色。
        mouse / keypad / mode 暂未实现具体行为, 仅保存。
        :param hwnd:    目标窗口句柄。
        :param display: 图色模式 (如 "gdi", "gdi2", "dx", "dx2" ...)。
        :param mouse:   鼠标模式 (如 "windows", "前台", ...)。
        :param keypad:  键盘模式 (如 "windows", "dx" ...)。
        :param mode:    绑定模式 (0=普通, 1=后台, 2=... 具体见大漠文档)。
        :return: True 成功, False 失败。
        """
        import win32gui  # 现成包 (pywin32): 提供窗口枚举/校验/几何信息

        # 0) 锁定 DPI 感知后再取坐标: 保证下面拿到的一定是设备像素,
        #    与截图换算 (设备 = 原点 + 客户区坐标 * scale) 保持同一空间。
        ensure_dpi_aware()

        # 1) 校验窗口句柄有效性
        if not hwnd or not win32gui.IsWindow(hwnd):
            return False

        # 2) 获取客户区原点与尺寸 (图色坐标原点基准; 均为设备像素)
        try:
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            ox, oy = win32gui.ClientToScreen(hwnd, (left, top))
        except Exception:
            return False

        # 3) 窗口可视边框原点: 窗口后台捕获的帧对齐基准。DWM 取不到时退回
        #    GetWindowRect 左上角 (Win10 及无 DWM 环境下两者一致)。
        origin = dwm_frame_origin(hwnd)
        if origin is None:
            try:
                wl, wt, _wr, _wb = win32gui.GetWindowRect(hwnd)
                origin = (wl, wt)
            except Exception:
                origin = (ox, oy)

        # 4) 换绑前先释放旧的捕获会话, 避免线程泄漏
        self._stop_capture()

        # 5) dx 类模式需要建立窗口后台捕获会话; 建不起来按大漠语义返回失败
        if display_backend(display) == "window":
            capture = WindowCapture(hwnd)
            if not capture.start():
                capture.stop()
                return False
            self._capture = capture

        # 6) 记录绑定状态 (其余参数暂存, 后续再实现具体逻辑)
        self.hwnd = hwnd
        self._bound = True
        self._client_origin = (ox, oy)
        self._client_size = (right - left, bottom - top)
        self._window_origin = origin
        self._display = display
        self._mouse = mouse
        self._keypad = keypad
        self._mode = mode
        return True

    def bind_window_ex(
        self,
        hwnd: int,
        display: str,
        mouse: str,
        keypad: str,
        mode: int,
        dx_inject: int = 0,
        dx_hook: int = 0,
        set_window_size: int = 0,
        width: int = 0,
        height: int = 0,
    ) -> bool:
        """
        绑定窗口 (大漠 BindWindowEx, 比 bind_window 多几个可选参数)。

        :param hwnd:    目标窗口句柄。
        :param display: 图色模式 (语义同 bind_window)。
        :param mouse:   鼠标模式。
        :param keypad:  键盘模式。
        :param mode:    绑定模式。
        :param dx_inject: 1=注入 (大漠付费功能), 本实现不支持, 仅记录。
        :param dx_hook:   1=hook 引擎 (大漠付费功能), 本实现不支持, 仅记录。
        :param set_window_size: 1=把窗口客户区调整为 width x height, 0=不调整。
        :param width:    目标宽度 (set_window_size=1 时生效)。
        :param height:   目标高度 (set_window_size=1 时生效)。
        :return: 绑定成功 True, 失败 False。
        """
        if set_window_size and width > 0 and height > 0:
            if not self._resize_client(hwnd, width, height):
                return False
        return self.bind_window(hwnd, display, mouse, keypad, mode)

    @staticmethod
    def _resize_client(hwnd: int, width: int, height: int) -> bool:
        """把窗口客户区调整为指定尺寸 (窗口矩形需加上非客户区占用的额外尺寸)。"""
        try:
            import win32con
            import win32gui

            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            wl, wt, wr, wb = win32gui.GetWindowRect(hwnd)
            # 非客户区 (边框 + 标题栏) 占用的额外尺寸
            extra_w = (wr - wl) - (right - left)
            extra_h = (wb - wt) - (bottom - top)
            win32gui.SetWindowPos(
                hwnd,
                0,
                0,
                0,
                int(width) + extra_w,
                int(height) + extra_h,
                win32con.SWP_NOZORDER | win32con.SWP_NOACTIVATE,
            )
            return True
        except Exception:
            return False



    def _stop_capture(self) -> None:
        """停止并释放窗口后台捕获会话 (无会话时为空操作)。"""
        capture, self._capture = self._capture, None
        if capture is not None:
            capture.stop()

    def un_bind_window(self) -> int:
        """
        解除当前绑定, 并释放窗口后台捕获会话。

        大漠要求脚本结束前调用, 否则后台绑定与捕获线程不会自动释放。
        :return: 1 成功, 0 失败 (本就未绑定时返回 0)。
        """
        if not self._bound:
            return 0
        self._stop_capture()
        self.hwnd = 0
        self._bound = False
        self._client_origin = (0, 0)
        self._client_size = (0, 0)
        self._window_origin = (0, 0)
        return 1

    def is_bind(self, hwnd: int) -> bool:
        """判断指定窗口是否已绑定。1 已绑定, 0 未绑定。"""
        return self._bound and hwnd == self.hwnd

    def set_sim_mode(self, mode: int) -> int:
        """
        设置图色后台兼容模式 (针对某些游戏的反截图保护)。
        :param mode: 0=普通, 1=兼容 gdi, 2=... 等。
        """
        ...

    def set_client_size(self, hwnd: int, width: int, height: int) -> int:
        """强制设置窗口客户区尺寸 (部分游戏需要)。"""
        ...

    def get_client_size(self, hwnd: int) -> str:
        """获取窗口客户区尺寸, 返回 "width|height"。"""
        ...

    def get_window_rect(self, hwnd: int, mode: int = 0) -> str:
        """获取窗口矩形, 返回 "left|top|right|bottom"。"""
        ...

    def get_window_state(self, hwnd: int, w_type: int) -> int:
        """
        获取窗口状态。取值语义对齐大漠 (pywin32 实现, 依赖 pywin32 现成包)。

        :param hwnd:   目标窗口句柄。
        :param w_type: 0=窗口是否存在, 1=是否激活(前台), 2=是否可见, 3=是否最小化,
                       4=是否最大化, 5=是否置顶, 6=是否无响应;
                       7/8/9 为大漠付费功能, 本实现不支持, 恒返回 0。
        :return: 1 满足条件, 0 不满足/失败。
        """
        import win32con
        import win32gui

        if not hwnd or not win32gui.IsWindow(hwnd):
            return 0
        if w_type == 0:
            return 1
        if w_type == 1:
            return int(win32gui.GetForegroundWindow() == hwnd)
        if w_type == 2:
            return int(bool(win32gui.IsWindowVisible(hwnd)))
        if w_type == 3:
            return int(bool(win32gui.IsIconic(hwnd)))
        if w_type == 4:
            return int(bool(win32gui.IsZoomed(hwnd)))
        if w_type == 5:
            ex = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            return int(bool(ex & win32con.WS_EX_TOPMOST))
        if w_type == 6:
            # 无响应判定: 给窗口发 WM_NULL 并要求"挂起即放弃", 超时即视为无响应
            try:
                result = win32gui.SendMessageTimeout(
                    hwnd, win32con.WM_NULL, 0, 0, win32con.SMTO_ABORTIFHUNG, 1000
                )
                return 0 if result is None else 1
            except Exception:
                return 0
        return 0

    def set_window_state(self, hwnd: int, flag: int) -> int:
        """
        设置窗口状态。取值语义对齐大漠 (pywin32 实现, 依赖 pywin32 现成包)。

        :param hwnd: 目标窗口句柄。
        :param flag: 0=关闭窗口, 1=激活, 2=最小化(不激活), 3=最小化并释放内存+激活,
                     4=最大化+激活, 5=还原(不激活), 6=隐藏, 7=显示, 8=置顶,
                     9=取消置顶, 10=禁止窗口, 11=取消禁止, 12=还原并激活,
                     13=强制结束窗口所属进程, 14/15=大漠付费功能, 本实现返回 0。
        :return: 1 成功, 0 失败/不支持。
        """
        import win32con
        import win32gui

        if not hwnd or not win32gui.IsWindow(hwnd):
            return 0
        try:
            if flag == 0:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            elif flag == 1:
                return int(self._activate(hwnd))
            elif flag == 2:
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            elif flag == 3:
                # 大漠语义: 最小化 + 释放内存 + 激活。释放内存在 win32 下以 psapi 实现。
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                self._empty_working_set(hwnd)
                return int(self._activate(hwnd))
            elif flag == 4:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                return int(self._activate(hwnd))
            elif flag == 5:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            elif flag == 6:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
            elif flag == 7:
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            elif flag == 8:
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW,
                )
            elif flag == 9:
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                    win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW,
                )
            elif flag == 10:
                win32gui.EnableWindow(hwnd, False)
            elif flag == 11:
                win32gui.EnableWindow(hwnd, True)
            elif flag == 12:
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                return int(self._activate(hwnd))
            elif flag == 13:
                return int(self._terminate_process(hwnd))
            else:
                # 14/15 及其他未知 flag: 大漠付费功能, 未实现
                return 0
            return 1
        except Exception:
            return 0

    @staticmethod
    def _activate(hwnd: int) -> bool:
        """
        激活并置前窗口。

        SetForegroundWindow 常因前台锁被系统拒绝, 故先 AttachThreadInput 借用前台线程
        的输入队列再试一次, 这是 win32 前台切换的通用做法。
        """
        import win32api
        import win32con
        import win32gui
        import win32process

        try:
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            if win32gui.SetForegroundWindow(hwnd):
                return True
            fg = win32gui.GetForegroundWindow()
            cur = win32api.GetCurrentThreadId()
            fg_tid = win32process.GetWindowThreadProcessId(fg)[0] if fg else cur
            attached = False
            try:
                attached = bool(win32process.AttachThreadInput(fg_tid, cur, True))
            except Exception:
                attached = False
            try:
                win32gui.BringWindowToTop(hwnd)
                win32gui.SetForegroundWindow(hwnd)
            finally:
                if attached:
                    try:
                        win32process.AttachThreadInput(fg_tid, cur, False)
                    except Exception:
                        pass
            return win32gui.GetForegroundWindow() == hwnd
        except Exception:
            return False

    @staticmethod
    def _empty_working_set(hwnd: int) -> None:
        """释放窗口所属进程的工作集 (大漠 flag=3 的"释放内存"); 失败静默忽略。"""
        try:
            import ctypes

            import win32process

            _tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            PROCESS_SET_QUOTA = 0x0100
            PROCESS_QUERY_INFORMATION = 0x0400
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_SET_QUOTA | PROCESS_QUERY_INFORMATION, False, pid
            )
            if handle:
                try:
                    ctypes.windll.psapi.EmptyWorkingSet(handle)
                finally:
                    ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            pass

    @staticmethod
    def _terminate_process(hwnd: int) -> bool:
        """强制结束窗口所属进程 (大漠 flag=13)。"""
        try:
            import ctypes

            import win32process

            _tid, pid = win32process.GetWindowThreadProcessId(hwnd)
            PROCESS_TERMINATE = 0x0001
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_TERMINATE, False, pid
            )
            if not handle:
                return False
            try:
                return bool(ctypes.windll.kernel32.TerminateProcess(handle, 1))
            finally:
                ctypes.windll.kernel32.CloseHandle(handle)
        except Exception:
            return False

    def set_display_input(self, mode: str) -> int:
        """设置图色输入来源 (如 "screen", "pic", "mem" 等, 用于调试)。"""
        ...

    def enable_display_input(self, mode: int) -> int:
        """开启/关闭显示输入 (调试用, 1 开启, 0 关闭)。"""
        ...

    def set_display_delay(self, delay: int) -> int:
        """设置图色操作的延时 (毫秒)。"""
        ...

    def set_display_index(self, index: int) -> int:
        """设置多显示器环境下的目标显示器索引。"""
        ...

    def get_screen_width(self) -> int:
        """获取屏幕 (或绑定窗口) 宽度。"""
        ...

    def get_screen_height(self) -> int:
        """获取屏幕 (或绑定窗口) 高度。"""
        ...
