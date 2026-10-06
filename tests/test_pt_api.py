"""
大漠插件 API 模拟层 —— 测试代码

说明:
    当前 dm_api 各模块仅为"方法桩" (函数体为 `...`, 无具体实现), 因此本测试聚焦于
    API 契约层面, 而非运行行为:
        1. 包与顶层类可正常导入、实例化。
        2. 顶层类 PtPlugin 通过 mixin 正确聚合了五个子模块。
        3. 每个模块的全部预期方法都存在于 PtPlugin 上 (防止误删/改名)。
        4. 部分代表方法的形参名与签名对齐大漠约定。
        5. 未实现的桩方法被调用时不会抛异常, 且返回 None (符合 `...` 占位语义)。

运行:
    cd 项目根目录
    python -m unittest discover -s tests
"""

from __future__ import annotations

import inspect
import os
import sys
import typing
import unittest

# 确保项目根目录在 sys.path 中 (无论从何处执行测试都能导入 dm_api)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from api import (  # noqa: E402
    BaseModule,
    ColorModule,
    ImageModule,
    DictionaryModule,
    InputControlModule,
    KeyboardModule,
    MouseModule,
    PtPlugin,
)
from api.base import display_backend  # noqa: E402
from api.color import client_rect_to_frame  # noqa: E402


def _cursor_control_available() -> bool:
    """检测当前环境是否允许真实光标控制 (远程/无光标会话会禁止 SetCursorPos)。"""
    try:
        import win32api

        x, y = win32api.GetCursorPos()
        win32api.SetCursorPos((x, y))
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# 各模块预期的方法清单 (作为 API 契约的"黄金标准")
# ---------------------------------------------------------------------------

EXPECTED_BASE = {
    "ver", "set_path", "bind_window", "bind_window_ex", "un_bind_window", "is_bind",
    "set_sim_mode", "set_client_size", "get_client_size", "get_window_rect",
    "get_window_state", "set_window_state", "set_display_input", "enable_display_input",
    "set_display_delay", "set_display_index", "get_screen_width", "get_screen_height",
}

EXPECTED_COLOR = {
    "get_color", "get_color_b_g_r", "get_color_h_s_v", "get_pixel_color", "cmp_color",
    "get_color_num", "get_color_count", "get_ave_r_g_b", "get_ave_h_s_v",
    "find_color", "find_color_ex", "find_color_e", "find_color_block",
    "find_multi_color", "find_multi_color_ex", "retry_find_color",
}

EXPECTED_IMAGE = {
    "find_pic", "find_pic_ex", "find_pic_mem", "find_pic_mem_ex", "find_pic_s",
    "find_pic_sim", "find_pic_addr", "find_pic_addr_ex", "get_pic_size",
    "retry_find_pic", "set_pic_find_scale", "set_pic_find_threshold",
    "enable_pic_cache", "set_cut_img_mode",
    "capture", "capture_png", "capture_jpg", "capture_memory",
    "get_screen_data", "get_screen_data_bmp",
}

EXPECTED_DICTIONARY = {
    "set_dict", "use_dict", "get_dict_count",
    "ocr", "ocr_ex", "ocr_auto", "ocr_auto_ex", "ocr_from_file",
    "find_str", "find_str_ex", "find_str_fast", "find_str_fast_ex",
    "find_str_s", "find_str_sim", "find_str_sim_ex",
    "get_words", "get_words_no_dict", "get_words_rate",
}

EXPECTED_MOUSE = {
    "move_to", "move_rel", "left_click", "left_down", "left_up", "right_click",
    "right_down", "right_up", "middle_click", "middle_down", "middle_up",
    "wheel_down", "wheel_up", "left_double_click", "right_double_click",
    "get_cursor_pos", "get_mouse_point", "get_mouse_point_window", "get_cursor_shape",
    "get_cursor_bunch", "match_cursor", "set_mouse_delay", "set_mouse_speed",
    "get_mouse_speed", "enable_mouse_sync", "enable_mouse_accuracy",
    "enable_real_mouse", "set_mouse_trail",
}

EXPECTED_KEYBOARD = {
    "key_press", "key_down", "key_up", "key_press_char", "key_press_str",
    "key_press_hex", "wait_key", "set_keypad_delay", "enable_keyboard_sync",
    "enable_real_keypad",
}

EXPECTED_INPUT_CONTROL = {
    "lock_input", "lock_display",
}

# 各模块 -> 预期方法集合
MODULE_EXPECTED = {
    "base": EXPECTED_BASE,
    "color": EXPECTED_COLOR,
    "image": EXPECTED_IMAGE,
    "dictionary": EXPECTED_DICTIONARY,
    "mouse": EXPECTED_MOUSE,
    "keyboard": EXPECTED_KEYBOARD,
    "input_control": EXPECTED_INPUT_CONTROL,
}


class TestImportAndAggregation(unittest.TestCase):
    """测试包导入与 mixin 聚合关系。"""

    def test_import_top_class(self):
        self.assertTrue(inspect.isclass(PtPlugin))

    def test_instantiate(self):
        inst = PtPlugin()
        self.assertIsInstance(inst, PtPlugin)

    def test_aggregates_all_modules(self):
        for mod in (
            BaseModule,
            ColorModule,
            ImageModule,
            DictionaryModule,
            MouseModule,
            KeyboardModule,
            InputControlModule,
        ):
            self.assertTrue(
                issubclass(PtPlugin, mod),
                f"PtPlugin 应继承 {mod.__name__}",
            )

    def test_submodules_importable(self):
        for mod in (
            BaseModule,
            ColorModule,
            ImageModule,
            DictionaryModule,
            MouseModule,
            KeyboardModule,
            InputControlModule,
        ):
            self.assertTrue(
                hasattr(mod, "ver")
                or hasattr(mod, "find_color")
                or hasattr(mod, "find_pic")
                or hasattr(mod, "set_dict")
                or hasattr(mod, "move_to")
                or hasattr(mod, "key_press")
                or hasattr(mod, "lock_input"),
                f"{mod.__name__} 应可独立导入",
            )


class TestApiSurface(unittest.TestCase):
    """测试每个模块的方法是否齐全 (API 契约)。"""

    def _check(self, module_name: str, expected: set):
        missing = expected - set(dir(PtPlugin))
        self.assertEqual(
            missing,
            set(),
            f"PtPlugin 缺少 {module_name} 模块的方法: {sorted(missing)}",
        )

    def test_base_methods(self):
        self._check("base", EXPECTED_BASE)

    def test_color_methods(self):
        self._check("color", EXPECTED_COLOR)

    def test_image_methods(self):
        self._check("image", EXPECTED_IMAGE)

    def test_dictionary_methods(self):
        self._check("dictionary", EXPECTED_DICTIONARY)

    def test_mouse_methods(self):
        self._check("mouse", EXPECTED_MOUSE)

    def test_keyboard_methods(self):
        self._check("keyboard", EXPECTED_KEYBOARD)

    def test_input_control_methods(self):
        self._check("input_control", EXPECTED_INPUT_CONTROL)

    def test_total_method_count(self):
        total_expected = sum(len(s) for s in MODULE_EXPECTED.values())
        # PtPlugin 上可调用 (非 dunder) 的方法数量应与契约一致
        # 注意: 方法来自各 mixin, 需用 dir() 才能取到继承来的方法 (vars 只含自身属性)
        public_methods = {
            name
            for name in dir(PtPlugin)
            if not name.startswith("_") and callable(getattr(PtPlugin, name))
        }
        self.assertEqual(len(public_methods), total_expected)


def _resolve_return(func):
    """解析函数返回类型注解 (兼容 from __future__ import annotations 的字符串注解)。"""
    return typing.get_type_hints(func).get("return")


class TestSignatures(unittest.TestCase):
    """测试代表方法的形参与返回类型注解是否对齐大漠约定。"""

    def test_findpic_signature(self):
        sig = inspect.signature(PtPlugin.find_pic)
        # 去掉实例方法首个参数 self
        params = list(sig.parameters)[1:]
        self.assertEqual(
            params,
            ["x1", "y1", "x2", "y2", "pic_name", "delta_color", "sim", "dir_"],
        )
        self.assertEqual(_resolve_return(PtPlugin.find_pic), str)

    def test_findcolor_signature(self):
        sig = inspect.signature(PtPlugin.find_color)
        params = list(sig.parameters)[1:]
        self.assertEqual(
            params, ["x1", "y1", "x2", "y2", "color", "sim", "dir_"]
        )
        ret = _resolve_return(PtPlugin.find_color)
        self.assertIs(typing.get_origin(ret), tuple)
        self.assertEqual(typing.get_args(ret), (bool, int, int))

    def test_moveto_signature(self):
        sig = inspect.signature(PtPlugin.move_to)
        self.assertEqual(list(sig.parameters)[1:], ["x", "y"])
        self.assertEqual(_resolve_return(PtPlugin.move_to), bool)

    def test_keypress_signature(self):
        sig = inspect.signature(PtPlugin.key_press)
        self.assertEqual(list(sig.parameters)[1:], ["key"])
        self.assertEqual(_resolve_return(PtPlugin.key_press), int)

    def test_bindwindow_signature(self):
        sig = inspect.signature(PtPlugin.bind_window)
        self.assertEqual(
            list(sig.parameters)[1:],
            ["hwnd", "display", "mouse", "keypad", "mode"],
        )


class TestStubBehavior(unittest.TestCase):
    """测试桩方法的行为: 调用不抛异常, 返回 None。"""

    def setUp(self):
        self.dm = PtPlugin()

    def test_stub_returns_none(self):
        # 各类代表方法调用后都应返回 None (因为函数体是 `...`)
        self.assertIsNone(self.dm.find_pic(0, 0, 10, 10, "a.bmp", "000000", 0.9))
        self.assertIsNone(self.dm.key_press(65))
        self.assertIsNone(self.dm.cmp_color(0, 0, "FFFFFF", 0.9))
        self.assertIsNone(self.dm.lock_input(1))

    def test_stub_accepts_various_args(self):
        # 验证可变参数桩 (如 find_pic_addr_ex / get_color_count) 不报错
        self.assertIsNone(self.dm.find_pic_addr_ex())
        self.assertIsNone(self.dm.get_color_count())
        self.assertIsNone(self.dm.capture_memory())
        self.assertIsNone(self.dm.set_mouse_trail(1, 2, 3))


class TestBindBehavior(unittest.TestCase):
    """测试 bind / bind_window 的真实绑定行为 (依赖 pywin32, 仅校验 hwnd 绑定)。"""

    def setUp(self):
        self.dm = PtPlugin()

    def test_bind_invalid_hwnd_returns_false(self):
        # 句柄为 0 或不存在的句柄都应绑定失败
        self.assertFalse(self.dm.bind_window(0, "gdi", "windows", "windows", 0))
        self.assertFalse(self.dm.bind_window(123456789, "gdi", "windows", "windows", 0))

    def test_bind_window_invalid_hwnd_returns_0(self):
        self.assertEqual(self.dm.bind_window(0, "gdi", "windows", "windows", 0), 0)

    def test_bind_valid_window_sets_state(self):
        import win32gui

        hwnd = win32gui.GetDesktopWindow()  # 桌面窗口一定有效
        self.assertTrue(self.dm.bind_window(hwnd, "gdi", "windows", "windows", 0))
        self.assertEqual(self.dm.hwnd, hwnd)
        self.assertTrue(self.dm._bound)
        self.assertEqual(len(self.dm._client_size), 2)


class TestMouseBehavior(unittest.TestCase):
    """测试 move_rel 的真实行为 (依赖 pywin32, 仅校验相对移动)。"""

    def setUp(self):
        self.dm = PtPlugin()
        if not _cursor_control_available():
            self.skipTest("SetCursorPos unavailable in this environment (remote/no-cursor session)")
        import win32api

        # 光标是全局 OS 状态, 复位到屏幕内部, 避免相对移动被边缘裁剪 (否则 Y 方向 delta 会被钳到 0)
        win32api.SetCursorPos((400, 400))

    def test_move_rel_zero_returns_1(self):
        # 原地相对移动应成功返回 1
        self.assertEqual(self.dm.move_rel(0, 0), 1)

    def test_move_rel_actual_offset(self):
        import win32api

        x0, y0 = win32api.GetCursorPos()
        dx, dy = 5, -7
        self.assertEqual(self.dm.move_rel(dx, dy), 1)
        x1, y1 = win32api.GetCursorPos()
        win32api.SetCursorPos((x0, y0))  # 还原光标, 避免干扰
        self.assertEqual((x1 - x0, y1 - y0), (dx, dy))


class TestMouseMode(unittest.TestCase):
    """测试 bind 的 mouse 模式: 前台真实事件生效, 后台/dx 模式留桩。"""

    def setUp(self):
        self.dm = PtPlugin()
        if not _cursor_control_available():
            self.skipTest("SetCursorPos unavailable in this environment (remote/no-cursor session)")
        import win32api

        win32api.SetCursorPos((400, 400))  # 同上, 复位光标避免边缘裁剪

    def test_move_to_default_is_foreground(self):
        # 未 bind 时 _mouse 为空 -> 前台模式, 应真实移动并返回 True
        self.assertTrue(self.dm.move_to(0, 0))

    def test_move_to_foreground_respects_bound_origin(self):
        import win32api, win32gui

        hwnd = win32gui.GetDesktopWindow()  # 桌面窗口一定有效
        self.dm.bind_window(hwnd, "gdi", "windows", "windows", 0)
        ox, oy = self.dm._client_origin
        self.assertTrue(self.dm.move_to(10, 20))
        x, y = win32api.GetCursorPos()
        win32api.SetCursorPos((0, 0))  # 还原光标, 避免干扰
        self.assertEqual((x - ox, y - oy), (10, 20))

    def test_move_to_background_mode_is_stub(self):
        import win32gui

        hwnd = win32gui.GetDesktopWindow()
        self.dm.bind_window(hwnd, "gdi", "dx", "windows", 0)  # mouse="dx" 后台模式
        # 后台/dx 模式暂未实现, 留桩: move_to 返回 False, move_rel 返回 False
        self.assertFalse(self.dm.move_to(10, 20))
        self.assertFalse(self.dm.move_rel(5, 5))


class TestFindColor(unittest.TestCase):
    """测试 find_color 的真实行为 (依赖 mss 截图 + 像素扫描)。"""

    def setUp(self):
        self.dm = PtPlugin()

    def test_find_color_invalid_color_returns_empty(self):
        # 非法颜色字符串应安全返回 (False, -1, -1) (不抛异常)
        self.assertEqual(self.dm.find_color(0, 0, 10, 10, "ZZ", 1.0), (False, -1, -1))

    def test_find_color_self_consistent(self):
        import mss

        # 抓屏幕 (0,0) 处 1x1 的颜色, 再在 [0,0,0,0] 内按该色严格查找, 应命中
        with mss.MSS() as sct:
            shot = sct.grab({"left": 0, "top": 0, "width": 1, "height": 1})
            rgb = shot.rgb
            r, g, b = rgb[0], rgb[1], rgb[2]
        target = f"{r:02X}{g:02X}{b:02X}"
        self.assertEqual(self.dm.find_color(0, 0, 0, 0, target, 1.0), (True, 0, 0))

    def test_find_color_bound_client_coords(self):
        import mss, win32gui

        hwnd = win32gui.GetDesktopWindow()
        self.dm.bind_window(hwnd, "gdi", "windows", "windows", 0)
        ox, oy = self.dm._client_origin
        # 客户区 (0,0) 对应屏幕 (ox,oy), 取该色后在客户区 (0,0) 严格查找应命中
        with mss.MSS() as sct:
            shot = sct.grab({"left": ox, "top": oy, "width": 1, "height": 1})
            rgb = shot.rgb
            r, g, b = rgb[0], rgb[1], rgb[2]
        target = f"{r:02X}{g:02X}{b:02X}"
        self.assertEqual(self.dm.find_color(0, 0, 0, 0, target, 1.0), (True, 0, 0))

    def test_find_color_ex_invalid_color_returns_empty(self):
        # 非法颜色应安全返回 [] (不抛异常)
        self.assertEqual(self.dm.find_color_ex(0, 0, 10, 10, "ZZ", 1.0), [])

    def test_find_color_ex_self_consistent(self):
        import mss

        # 抓屏幕 (0,0) 处 1x1 的颜色, 再在 [0,0,0,0] 内按该色严格查找, 应得 [(0,0)]
        with mss.MSS() as sct:
            shot = sct.grab({"left": 0, "top": 0, "width": 1, "height": 1})
            rgb = shot.rgb
            r, g, b = rgb[0], rgb[1], rgb[2]
        target = f"{r:02X}{g:02X}{b:02X}"
        self.assertEqual(self.dm.find_color_ex(0, 0, 0, 0, target, 1.0), [(0, 0)])

    def test_find_color_ex_all_pixels_when_sim_zero(self):
        # sim=0.0 -> 每通道容差 255, 区域内每个像素都视为匹配
        # dir_=0 扫描顺序: 左->右, 上->下 -> 2x2 区域应返回全部 4 个坐标
        res = self.dm.find_color_ex(0, 0, 1, 1, "000000", 0.0)
        self.assertEqual(res, [(0, 0), (1, 0), (0, 1), (1, 1)])


class TestDisplayBackend(unittest.TestCase):
    """测试 bind 的 display 参数 -> 捕获后端映射 (api.base.display_backend)。"""

    def test_screen_modes(self):
        for d in ("normal", "gdi", "gdi2", "gdi3"):
            self.assertEqual(display_backend(d), "screen", d)

    def test_window_modes(self):
        for d in ("dx", "dx2", "dx3", "dx2.0", "dx.graphic.2d"):
            self.assertEqual(display_backend(d), "window", d)

    def test_none_mode(self):
        for d in ("none", "null"):
            self.assertEqual(display_backend(d), "none", repr(d))

    def test_empty_defaults_to_screen(self):
        # 未绑定时 _display 为空串 -> 必须仍能整屏抓图 (保持旧行为)
        self.assertEqual(display_backend(""), "screen")

    def test_case_insensitive_and_unknown_fallback(self):
        self.assertEqual(display_backend("DX2"), "window")
        self.assertEqual(display_backend(" gdi "), "screen")
        # 未知写法退回整屏, 保证 bind 不因写法差异直接失败
        self.assertEqual(display_backend("whatever"), "screen")


class TestClientRectToFrame(unittest.TestCase):
    """测试客户区逻辑坐标 -> WGC 帧内像素的换算 (半开区间 + 边界裁剪)。"""

    def test_basic_without_scale(self):
        # 客户区原点 (100,200), 窗口可视边框原点 (92,200) -> 帧内客户区起点 (8,0)
        rect = client_rect_to_frame(
            0, 0, 9, 9,
            client_origin=(100, 200), window_origin=(92, 200),
            scale=1.0, frame_size=(1000, 1000),
        )
        # 闭区间 0..9 共 10 px -> 半开 [8, 18)
        self.assertEqual(rect, (8, 0, 18, 10))

    def test_dpi_scale_applied(self):
        # 150% 缩放: 逻辑 0..9 (10px) -> 15 设备像素
        rect = client_rect_to_frame(
            0, 0, 9, 9,
            client_origin=(100, 200), window_origin=(100, 200),
            scale=1.5, frame_size=(1000, 1000),
        )
        self.assertEqual(rect, (0, 0, 15, 15))

    def test_clipped_to_frame(self):
        rect = client_rect_to_frame(
            -50, -50, 9, 9,
            client_origin=(100, 100), window_origin=(100, 100),
            scale=1.0, frame_size=(40, 40),
        )
        self.assertEqual(rect, (0, 0, 10, 10))

    def test_no_overlap_returns_none(self):
        rect = client_rect_to_frame(
            500, 500, 600, 600,
            client_origin=(100, 100), window_origin=(100, 100),
            scale=1.0, frame_size=(200, 200),
        )
        self.assertIsNone(rect)


class TestBindBackend(unittest.TestCase):
    """测试 bind 按 display 选择后端, 以及解绑。"""

    def setUp(self):
        import win32gui

        self.dm = PtPlugin()
        self.hwnd = win32gui.GetDesktopWindow()

    def test_is_bind_before_bind_is_false(self):
        # 未绑定时调用不应抛 AttributeError (hwnd 属性已在 __init__ 初始化)
        self.assertFalse(self.dm.is_bind(self.hwnd))

    def test_bind_none_display_disables_grab(self):
        self.assertTrue(self.dm.bind_window(self.hwnd, "none", "windows", "windows", 0))
        # display="none" 表示不绑定图色 -> 抓图为空, 找色安全返回未找到
        self.assertIsNone(self.dm._grab_region(0, 0, 10, 10))
        self.assertEqual(self.dm.find_color(0, 0, 10, 10, "FFFFFF", 1.0), (False, -1, -1))

    def test_bind_screen_display_has_no_capture_session(self):
        self.assertTrue(self.dm.bind_window(self.hwnd, "gdi", "windows", "windows", 0))
        self.assertIsNone(self.dm._capture)

    def test_un_bind_window(self):
        self.assertTrue(self.dm.bind_window(self.hwnd, "gdi", "windows", "windows", 0))
        self.assertTrue(self.dm.is_bind(self.hwnd))
        self.assertEqual(self.dm.un_bind_window(), 1)
        self.assertFalse(self.dm.is_bind(self.hwnd))
        self.assertEqual(self.dm.hwnd, 0)
        # 重复解绑返回 0
        self.assertEqual(self.dm.un_bind_window(), 0)

    def test_switch_display_releases_previous_capture(self):
        # 先绑窗口后台(桌面窗口通常不可被 WGC 捕获, 允许绑定失败), 再绑整屏, 应始终可用
        self.dm.bind_window(self.hwnd, "dx", "windows", "windows", 0)
        self.assertTrue(self.dm.bind_window(self.hwnd, "gdi", "windows", "windows", 0))
        self.assertIsNone(self.dm._capture)


class TestWindowState(unittest.TestCase):
    """测试 get_window_state / set_window_state (依赖 pywin32)。"""

    def setUp(self):
        import win32gui

        self.dm = PtPlugin()
        self.hwnd = win32gui.GetDesktopWindow()  # 桌面窗口一定存在

    def test_get_state_exists_and_visible(self):
        self.assertEqual(self.dm.get_window_state(self.hwnd, 0), 1)
        self.assertEqual(self.dm.get_window_state(self.hwnd, 2), 1)

    def test_get_state_invalid_hwnd(self):
        self.assertEqual(self.dm.get_window_state(0, 0), 0)
        self.assertEqual(self.dm.get_window_state(123456789, 0), 0)

    def test_get_state_paid_types_return_0(self):
        # 7/8/9 属大漠付费功能, 本实现不支持
        for w_type in (7, 8, 9):
            self.assertEqual(self.dm.get_window_state(self.hwnd, w_type), 0)

    def test_set_state_invalid_hwnd(self):
        self.assertEqual(self.dm.set_window_state(0, 1), 0)
        self.assertEqual(self.dm.set_window_state(123456789, 1), 0)

    def test_set_state_restore(self):
        # flag=5 还原(不激活): 桌面窗口上是无害操作
        self.assertEqual(self.dm.set_window_state(self.hwnd, 5), 1)

    def test_set_state_paid_flags_return_0(self):
        # 14/15 为大漠付费功能
        self.assertEqual(self.dm.set_window_state(self.hwnd, 14), 0)
        self.assertEqual(self.dm.set_window_state(self.hwnd, 15), 0)

    def test_set_state_enable_disable(self):
        # flag=10 禁止 / 11 取消禁止 (桌面窗口上无害, 仅验证调用链)
        self.assertEqual(self.dm.set_window_state(self.hwnd, 11), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
