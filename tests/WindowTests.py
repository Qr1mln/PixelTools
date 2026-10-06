import logging
import unittest

import cv2
import numpy as np

from api import PTPlugin
logging.basicConfig(level=logging.INFO)

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

    def test_screenshot(self):
        pt = PTPlugin()
        self.assertTrue(pt.bind_window(title="Last Epoch", clazz="UnityWndClass"), "绑定窗口失败")
        img = pt.screenshot()
        logging.info(f"Screenshot shape: {img.shape}")
        #cv2.imshow("img",cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        #cv2.waitKey(0)
        self.assertTrue(img.shape == (2160, 3840, 3))
        self.assertTrue(img.dtype == np.uint8)

    def test_screenshot_client(self):
        pt = PTPlugin()
        self.assertTrue(pt.bind_window(title="Last Epoch", clazz="UnityWndClass"), "绑定窗口失败")
        img = pt.screenshot(446,979,575,997)
        logging.info(f"Screenshot shape: {img.shape}")
        cv2.imshow("img",cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        cv2.waitKey(0)
        self.assertTrue(img.shape == (18, 129, 3))
        self.assertTrue(img.dtype == np.uint8)

