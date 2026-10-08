import logging
import unittest

import cv2
import numpy as np

from PyAutoPlugin import Plugin
logging.basicConfig(level=logging.INFO)

class TestWindow(unittest.TestCase):

    def test_bind_window_for_not_valid_hwnd(self):
        
        self.assertFalse(Plugin.bind_window(hwnd=12223))

    def test_bind_window_for_valid_hwnd(self):
        
        self.assertTrue(Plugin.bind_window(hwnd=4135884))

    def test_bind_window_for_not_valid_title_class(self):
        
        self.assertFalse(Plugin.bind_window(title="132133", clazz="24234234"), "绑定窗口失败")

    def test_bind_window_for_valid_title_class(self):
        
        self.assertTrue(Plugin.bind_window(title="Last Epoch", clazz="UnityWndClass"), "绑定窗口失败")

    def test_bind_window_for_valid_info(self):
        
        self.assertTrue(Plugin.bind_window(title="Last Epoch", clazz="UnityWndClass"), "绑定窗口失败")
        self.assertEqual(Plugin.hwnd, 4135884)
        self.assertTrue(Plugin.ox != 0)
        self.assertTrue(Plugin.oy != 0)

    def test_screenshot(self):
        
        self.assertTrue(Plugin.bind_window(title="Last Epoch", clazz="UnityWndClass"), "绑定窗口失败")
        img = Plugin.screenshot()
        logging.info(f"Screenshot shape: {img.shape}")
        #cv2.imshow("img",cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        #cv2.waitKey(0)
        self.assertTrue(img.shape == (2160, 3840, 3))
        self.assertTrue(img.dtype == np.uint8)

    def test_screenshot_client(self):
        
        self.assertTrue(Plugin.bind_window(title="Last Epoch", clazz="UnityWndClass"), "绑定窗口失败")
        img = Plugin.screenshot(845, 948, 1045, 1048)
        logging.info(f"Screenshot shape: {img.shape}")
        #cv2.imshow("img",cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
        #cv2.waitKey(0)
        self.assertTrue(img.shape == (18, 129, 3))
        self.assertTrue(img.dtype == np.uint8)

