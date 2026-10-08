import unittest

import time

from PyAutoPlugin import Plugin


class OcrTests(unittest.TestCase):
    def test_ocr_image(self):
        Plugin.bind_window(title="Last Epoch", clazz="UnityWndClass")
        result = Plugin.ocr(478, 970, 548, 1003)
        print(result)
