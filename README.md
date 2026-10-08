# PixelTools

Windows 下的窗口截图、颜色查找、OCR 文字识别工具集，专为游戏 / 桌面自动化脚本设计。
通过 `Plugin` 聚合类统一对外提供能力，所有方法均为类方法，无需实例化。

> ⚠️ **仅支持 Windows**。底层依赖 `pywin32` 与 `windows-capture` 进行窗口绑定与截图，且 `screenshot` 基于 `mss`。

## 名称说明

| 概念 | 值 | 说明 |
| --- | --- | --- |
| 项目名 | `PixelTools` | 本仓库 / 文档称呼 |
| PyPI 发行名 | `PyAutoPlugin` | `pip install` 使用的名字（`pip install PyAutoPlugin`） |
| 导入名（包名） | `PyAutoPlugin` | 代码里 `import` 的名字，例如 `from PyAutoPlugin import Plugin` |

## 环境要求

- Windows 10 / 11
- Python >= 3.12
- 已安装对应 Python 版本的 `pywin32`（安装包后会自动作为依赖拉取）

## 安装

从 PyPI 安装：

```bash
pip install PyAutoPlugin
```

导入方式：

```python
from PyAutoPlugin import Plugin
```

## 快速上手

```python
from PyAutoPlugin import Plugin, Ocr

# 1. 绑定目标窗口（按标题 + 类名查找；也可直接传 hwnd）
Plugin.bind_window(title="Last Epoch", clazz="UnityWndClass")

# 2. 区域截图（客户区坐标，DPI 自动换算）
img = Plugin.screenshot(478, 970, 548, 1003)

# 3. OCR 识别（需先配置自建 OCR 服务地址）
Ocr.url = "http://127.0.0.1:9000/ocr"
items = Plugin.ocr(478, 970, 548, 1003)
for it in items:
    print(it.text, it.score, it.box)

# 4. 颜色查找
x, y = Plugin.findColor(0, 0, 800, 600, "e9e8e8-000000", sim=0.9)
print("found at", x, y)

# 5. 多点找色，返回所有命中
points = Plugin.findMultiColorEx(
    0, 0, 800, 600,
    first_color="e9e8e8-000000",
    offset_colors="10|5|ffffff-101010,20|0|123456-000000",
    sim=0.9,
)

# 6. 预览截图（会弹 OpenCV 窗口，按任意键关闭）
Plugin.preview(img, x=x, y=y)

# 用完解绑
Plugin.unbind_window()
```

## API 参考

### 窗口 Window

| 方法 | 说明 |
| --- | --- |
| `bind_window(hwnd=0, title=None, clazz=None, display="normal", mouse="normal", keypad="normal", mode=0)` | 绑定窗口。传 `hwnd` 直接绑定；否则按 `title`(包含匹配) / `clazz`(精确匹配) 查找。返回 `True/False`。 |
| `unbind_window()` | 解除绑定，清空 `hwnd/ox/oy/is_bind`。 |
| `screenshot(x1=None, y1=None, x2=None, y2=None)` | 全屏或指定客户区区域截图，返回 `(H, W, 3)` 的 `uint8` RGB 数组。坐标为客户区逻辑坐标，DPI 已自动换算。 |

### OCR Ocr

走自建 / 通用 HTTP 接口：把截图编码为图片字节后 base64，POST 给 `Ocr.url`，返回 PP-Structure / PaddleOCR 风格结构。

| 配置项 | 说明 |
| --- | --- |
| `Ocr.url` | OCR 服务地址，必填。 |
| `Ocr.headers` | 鉴权 / 自定义请求头。 |
| `Ocr.timeout` | 请求超时（秒），默认 10。 |
| `Ocr.image_format` | 编码格式，默认 `.png`。 |

| 方法 | 返回 |
| --- | --- |
| `ocr(x1, y1, x2, y2)` | `list[OcrItem]`，每项含 `text: str`、`score: float`、`box: list`（取自接口原始 `rec_boxes`）。未配置地址或请求失败返回 `[]`。 |

### 找色 Color

颜色格式为 `"RRGGBB-DRDGDB"`（与按键精灵相反），多色用 `|` 分隔；偏色全 0 且给定 `sim` 时，用相似度推导三通道总差容差，使 `sim` 真正生效。

| 方法 | 返回 | 说明 |
| --- | --- | --- |
| `findColor(x1, y1, x2, y2, color, sim=None, mode=0)` | `(x, y)` 或 `(-1, -1)` | 区域内找首个匹配主色点。`mode` 控制查找方向（0~8）。 |
| `findMultiColor(x1, y1, x2, y2, first_color, offset_colors, sim=0.9, mode=0)` | `(x, y)` 或 `(-1, -1)` | 主色 + 偏移点全部满足才命中。 |
| `findMultiColorEx(x1, y1, x2, y2, first_color, offset_colors, sim=0.9, max_count=1800)` | `[(x, y), ...]` | 返回所有命中点，最多 `max_count` 个。 |

`offset_colors` 格式：`"dx|dy|RRGGBB-DRDGDB,dx|dy|..."`，例如 `"10|5|ffffff-101010"`。

### 调试 Debug

| 方法 | 说明 |
| --- | --- |
| `preview(img_rgb, title="PixelTools", x=None, y=None, points=None, wait=0, color=(0,0,255))` | 用 OpenCV 显示 RGB 截图，可选在 `(x, y)` 处画十字+圆圈标记。 |

## 配置 OCR 服务

`ocr()` 依赖外部 OCR 服务（本项目不含模型）。使用前设置：

```python
from PyAutoPlugin import Ocr

Ocr.url = "http://127.0.0.1:9000/ocr"
Ocr.headers = {"Authorization": "Bearer <你的token>"}   # 如服务需要鉴权
```

返回结构约定（PP-Structure / PaddleOCR 风格）：

```
result.ocrResults[0].prunedResult.rec_texts   -> list[str]  按行/块文本
result.ocrResults[0].prunedResult.rec_scores  -> list[float] 置信度 0~1
result.ocrResults[0].prunedResult.rec_boxes   -> list        原始文本框
```

## 注意事项

- **全局单例状态**：`hwnd/ox/oy/is_bind` 为类级变量，一个进程内只能绑定一个窗口。多窗口场景请使用多个独立进程。
- **DPI 感知**：绑定时会开启进程 DPI 感知，保证 `ClientToScreen` 与 `mss` 坐标统一为物理像素，无需手动乘缩放系数。
- **Windows-only**：非 Windows 平台无法安装 / 运行核心功能。


