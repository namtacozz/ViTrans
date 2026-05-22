from functools import lru_cache

from vitrans.encoding import configure_utf8_stdio

configure_utf8_stdio()

import easyocr
import numpy as np
from PIL import Image

from vitrans.models import OcrResult, Rect


@lru_cache(maxsize=1)
def get_reader() -> easyocr.Reader:
    return easyocr.Reader(["en"], gpu=False)


def warm_up_reader() -> None:
    get_reader()


def _bbox_to_rect(points: list[list[float]]) -> Rect:
    xs = [int(point[0]) for point in points]
    ys = [int(point[1]) for point in points]
    min_x = min(xs)
    min_y = min(ys)
    return Rect(x=min_x, y=min_y, width=max(xs) - min_x, height=max(ys) - min_y)


def read_text(image: Image.Image, min_confidence: float = 0.35) -> list[OcrResult]:
    reader = get_reader()
    raw_results = reader.readtext(np.array(image))
    results: list[OcrResult] = []
    for points, text, confidence in raw_results:
        clean_text = text.strip()
        if not clean_text or confidence < min_confidence:
            continue
        results.append(OcrResult(text=clean_text, confidence=float(confidence), bbox=_bbox_to_rect(points)))
    return results
