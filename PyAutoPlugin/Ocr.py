import base64
import logging
import uuid
from dataclasses import dataclass

import cv2
import numpy as np
import requests

logger = logging.getLogger(__name__)


@dataclass
class OcrItem:
    """单条 OCR 识别结果。"""
    text: str
    score: float
    box: list  # 直接取自 rec_boxes 的原始框

class Ocr:
    """OCR 文字识别 mixin。

    走自建/通用 HTTP 接口，约定请求体为 JSON：
        {"image": "<图片字节的 base64 字符串>"}

    使用前配置服务地址与鉴权（类级属性，也可在子类里覆盖）：
        Ocr.url = "http://127.0.0.1:8000/ocr"
        Ocr.headers = {"Authorization": "Bearer xxx"}
    """

    # ---- 可配置项 ----
    url: str = "http://127.0.0.1:9000/ocr"              # OCR 服务地址
    headers: dict = {}         # 鉴权 / 自定义请求头
    timeout: float = 10.0      # 请求超时（秒）
    image_format: str = ".png" # 编码格式；文本识别建议 png 无损

    def __init__(self):
        ...

    @classmethod
    def ocr(cls,x1: int, y1: int, x2: int, y2: int) -> list[OcrItem]:
        """识别图片中的文字并返回文本。

        参数:
            img: (H, W, 3) 的 uint8 RGB 数组（来自 screenshot）。

        返回:
            识别文本；未配置地址或请求失败时返回空字符串。
        """
        if not cls.url:
            logger.error("未配置 OCR 服务地址：请设置 Ocr.url")
            return []

        # 1. 归一化为 uint8
        from PyAutoPlugin import Plugin
        img = np.asarray(Plugin.screenshot(x1, y1, x2, y2))
        if img.dtype != np.uint8:
            img = np.clip(img, 0, 255).astype(np.uint8)

        # 2. 编码为图片字节（接口要的是 JPEG/PNG 编码，而非原始像素字节）
        ok, buf = cv2.imencode(cls.image_format, img)
        if not ok:
            logger.error("图片编码失败")
            return ""

        # 3. 转 base64
        img_base64 = base64.b64encode(buf.tobytes()).decode("ascii")
        uid = uuid.uuid4()
        # 4. 调用接口
        payload = {
            "file":img_base64,
            "fileType": 1,
            "useDocOrientationClassify": True,
            "useDocUnwarping": True,
            "useTextlineOrientation": True,
            "textDetLimitSideLen": 0,
            "textDetLimitType": "min",
            "textDetThresh": 0,
            "textDetBoxThresh": 0,
            "textDetUnclipRatio": 0,
            "textRecScoreThresh": 0,
            "returnWordBox": True,
            "visualize": False,
            "logId": str(uid)
        }
        try:
            resp = requests.post(
                cls.url,
                json=payload,
                headers=cls.headers,
                timeout=cls.timeout,
            )
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"OCR 请求失败: {e}")
            return []

        # 5. 解析返回文本
        return cls._parse(resp.json())



    @classmethod
    def _parse(cls, data) -> list[OcrItem]:
        if not isinstance(data, dict):
            return []
        if data.get("errorCode", 0) != 0:
            logger.error(f"OCR 服务返回失败: {data.get('errorCode')} {data.get('errorMsg')}")
            return []

        ocr_results = data.get("result", {}).get("ocrResults", [])
        if not ocr_results:
            return []

        pruned = ocr_results[0].get("prunedResult", {})
        texts = pruned.get("rec_texts", [])
        scores = pruned.get("rec_scores", [])
        boxes = pruned.get("rec_boxes", [])

        items = []
        for i, text in enumerate(texts):
            score = scores[i] if i < len(scores) else 0.0
            box = boxes[i] if i < len(boxes) else []
            items.append(OcrItem(text=str(text), score=float(score), box=box))
        return items

