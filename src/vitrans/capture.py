from PIL import Image
from mss import mss

from vitrans.models import Rect


def capture_rect(rect: Rect) -> Image.Image:
    monitor = {
        "left": rect.x,
        "top": rect.y,
        "width": rect.width,
        "height": rect.height,
    }
    with mss() as screen_capture:
        screenshot = screen_capture.grab(monitor)
    return Image.frombytes("RGB", screenshot.size, screenshot.rgb)
