"""基础 / 窗口绑定模块 —— 使用图色与键鼠前通常需要先绑定窗口。"""

from __future__ import annotations


class BaseModule:
    """基础与窗口绑定相关方法 (大漠 API 模拟桩)。"""

    # ---------------------------------------------------------------------
    # 版本 / 路径
    # ---------------------------------------------------------------------

    def Ver(self) -> str:
        """获取当前大漠插件版本号, 例如 "3.1238"。"""
        ...

    def SetPath(self, path: str) -> int:
        """
        设置大漠插件的全局路径 (字库、图片资源等所在目录)。
        :param path: 资源目录的绝对路径。
        :return: 1 成功, 0 失败。
        """
        ...

    # ---------------------------------------------------------------------
    # 窗口绑定
    # ---------------------------------------------------------------------

    def BindWindow(
        self,
        hwnd: int,
        display: str,
        mouse: str,
        keypad: str,
        mode: int,
    ) -> int:
        """
        绑定指定的窗口, 使其接受大漠的图色/鼠标/键盘操作。
        :param hwnd:    目标窗口句柄。
        :param display: 图色模式 (如 "gdi", "gdi2", "dx", "dx2" ...)。
        :param mouse:   鼠标模式 (如 "windows", "windows2", "dx" ...)。
        :param keypad:  键盘模式 (如 "windows", "dx" ...)。
        :param mode:    绑定模式 (0=普通, 1=后台, 2=... 具体见大漠文档)。
        :return: 1 成功, 0 失败。
        """
        ...

    def BindWindowEx(
        self,
        hwnd: int,
        display: str,
        mouse: str,
        keypad: str,
        public: str,
        mode: int,
    ) -> int:
        """
        扩展绑定窗口, 比 BindWindow 多一个 public 参数 (公共/前台模式)。
        :param public: 公共模式字符串 (如 "windows", "dx.public" ...)。
        :return: 1 成功, 0 失败。
        """
        ...

    def UnBindWindow(self) -> int:
        """解除当前绑定。"""
        ...

    def IsBind(self, hwnd: int) -> int:
        """判断指定窗口是否已绑定。1 已绑定, 0 未绑定。"""
        ...

    # ---------------------------------------------------------------------
    # 兼容模式 / 窗口状态
    # ---------------------------------------------------------------------

    def SetSimMode(self, mode: int) -> int:
        """
        设置图色后台兼容模式 (针对某些游戏的反截图保护)。
        :param mode: 0=普通, 1=兼容 gdi, 2=... 等。
        """
        ...

    def SetClientSize(self, hwnd: int, width: int, height: int) -> int:
        """强制设置窗口客户区尺寸 (部分游戏需要)。"""
        ...

    def GetClientSize(self, hwnd: int) -> str:
        """获取窗口客户区尺寸, 返回 "width|height"。"""
        ...

    def GetWindowRect(self, hwnd: int, mode: int = 0) -> str:
        """获取窗口矩形, 返回 "left|top|right|bottom"。"""
        ...

    def GetWindowState(self, hwnd: int, w_type: int) -> int:
        """获取窗口状态 (如是否最小化/最大化/前台等)。"""
        ...

    def SetWindowState(self, hwnd: int, flag: int) -> int:
        """设置窗口状态 (最小化/还原/最大化/置顶等)。"""
        ...

    # ---------------------------------------------------------------------
    # 显示输入 / 多屏
    # ---------------------------------------------------------------------

    def SetDisplayInput(self, mode: str) -> int:
        """设置图色输入来源 (如 "screen", "pic", "mem" 等, 用于调试)。"""
        ...

    def EnableDisplayInput(self, mode: int) -> int:
        """开启/关闭显示输入 (调试用, 1 开启, 0 关闭)。"""
        ...

    def SetDisplayDelay(self, delay: int) -> int:
        """设置图色操作的延时 (毫秒)。"""
        ...

    def SetDisplayIndex(self, index: int) -> int:
        """设置多显示器环境下的目标显示器索引。"""
        ...

    def GetScreenWidth(self) -> int:
        """获取屏幕 (或绑定窗口) 宽度。"""
        ...

    def GetScreenHeight(self) -> int:
        """获取屏幕 (或绑定窗口) 高度。"""
        ...
