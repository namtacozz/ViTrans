from dataclasses import dataclass


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class OcrResult:
    text: str
    confidence: float
    bbox: Rect


@dataclass(frozen=True)
class TranslatedBox:
    original: str
    translated: str
    bbox: Rect
