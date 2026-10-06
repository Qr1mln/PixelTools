import unittest

from api import PTPlugin

class TestWindow(unittest.TestCase):

    def test_bind_window_for_not_valid_hwnd(self):
        pt = PTPlugin()
        self.assertFalse(pt.bind_window(hwnd=12223))

    def test_bind_window_for_valid_hwnd(self):
        pt = PTPlugin()
        self.assertTrue(pt.bind_window(hwnd=4135884))

    def test_bind_window_for_not_valid_title_class(self):
        pt = PTPlugin()
        self.assertFalse(pt.bind_window(title="132133", clazz="24234234"), "绑定窗口失败")

    def test_bind_window_for_valid_title_class(self):
        pt = PTPlugin()
        self.assertTrue(pt.bind_window(title="Last Epoch", clazz="UnityWndClass"), "绑定窗口失败")

    def test_bind_window_for_valid_info(self):
        pt = PTPlugin()
        self.assertTrue(pt.bind_window(title="Last Epoch", clazz="UnityWndClass"), "绑定窗口失败")
        self.assertEqual(pt.hwnd, 4135884)
        self.assertTrue(pt.ox!=0)
        self.assertTrue(pt.oy!=0)