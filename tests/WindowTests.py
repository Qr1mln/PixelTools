import unittest

from api import PTPlugin

class TestWindow(unittest.TestCase):

    def test_bind_window_for_not_valid_hwnd(self):
        pt = PTPlugin()
        self.assertFalse(pt.bind(hwnd=12223))

    def test_bind_window_for_valid_hwnd(self):
        pt = PTPlugin()
        self.assertTrue(pt.bind(hwnd=4135884))

    def test_bind_window_for_not_valid_title_class(self):
        pt = PTPlugin()
        self.assertTrue(pt.bind(title="132133",clazz="24234234"),"绑定窗口失败")

    def test_bind_window_for_valid_title_class(self):
        pt = PTPlugin()
        self.assertTrue(pt.bind(title="Last Epoch",clazz="UnityWndClass"),"绑定窗口失败")