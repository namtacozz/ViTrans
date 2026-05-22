# ViTrans Fast White Rendering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve perceived translation speed and render translated text as white text sized/positioned from OCR boxes without black background blocks.

**Architecture:** Keep OCR, translation, and rendering separate. Add deterministic font-size geometry helper, cache translations in `translate.py`, warm up EasyOCR in a background thread during app startup, and render per-box white text with bbox-derived font size.

**Tech Stack:** Python 3.12, PyQt6, EasyOCR, deep-translator, pytest.

---

## File Structure

- `src/vitrans/models.py`: add `font_size` to `TranslatedBox`.
- `src/vitrans/geometry.py`: add `font_size_for_bbox` helper.
- `tests/test_geometry.py`: test font size calculation.
- `src/vitrans/translate.py`: add in-memory cache for repeated text translations.
- `src/vitrans/ocr.py`: add `warm_up_reader` alias for startup warm-up.
- `src/vitrans/main.py`: start OCR warm-up thread and set per-box font size.
- `src/vitrans/overlay.py`: remove black fill; draw white text with subtle shadow/outline.
- `README.md`: document speed/rendering behavior.

## Task 1: Font Size From OCR BBox

**Files:**
- Modify: `src/vitrans/models.py`
- Modify: `src/vitrans/geometry.py`
- Modify: `tests/test_geometry.py`

- [ ] Add `font_size: int` field to `TranslatedBox`.
- [ ] Add `font_size_for_bbox(bbox: Rect) -> int` returning `max(10, min(32, int(bbox.height * 0.85)))`.
- [ ] Add tests for small/normal/large bbox heights.
- [ ] Run `. .venv312/Scripts/activate && PYTHONPATH=src python -m pytest tests/test_geometry.py -v` expecting pass.

## Task 2: Translation Cache

**Files:**
- Modify: `src/vitrans/translate.py`

- [ ] Add module-level cache keyed by `(target_language, text)`.
- [ ] Return cached translations immediately when all texts exist.
- [ ] Only send uncached texts to `GoogleTranslator.translate_batch`.
- [ ] Preserve order of input texts in returned list.
- [ ] Run import smoke check: `. .venv312/Scripts/activate && PYTHONPATH=src python -c "from vitrans.translate import translate_texts; print(translate_texts([]))"` expecting `[]`.

## Task 3: OCR Warm-Up

**Files:**
- Modify: `src/vitrans/ocr.py`
- Modify: `src/vitrans/main.py`

- [ ] Add `warm_up_reader() -> None` that calls `get_reader()`.
- [ ] In app `__init__`, start daemon `threading.Thread(target=warm_up_reader)` after creating tray/hotkey state.
- [ ] Run import smoke check: `. .venv312/Scripts/activate && PYTHONPATH=src python -c "from vitrans.main import ViTransApp; print(ViTransApp.__name__)"` expecting `ViTransApp`.

## Task 4: White Text Rendering

**Files:**
- Modify: `src/vitrans/main.py`
- Modify: `src/vitrans/overlay.py`

- [ ] In `translate_selection`, create `TranslatedBox(..., font_size=font_size_for_bbox(result.bbox))`.
- [ ] In overlay `paintEvent`, remove `painter.fillRect(... QColor(0, 0, 0, 190))`.
- [ ] Draw translated text in white using `QFont("Segoe UI", item.font_size)`.
- [ ] Draw same text once behind with semi-transparent dark pen offset by 1px for readability; no black rectangle.
- [ ] Run import smoke check: `. .venv312/Scripts/activate && PYTHONPATH=src python -c "from vitrans.overlay import OverlayWindow; from vitrans.main import ViTransApp; print('ok')"` expecting `ok`.

## Task 5: README, Tests, Commit

**Files:**
- Modify: `README.md`

- [ ] Add note that app warms OCR in background and renders white translated text sized from OCR boxes.
- [ ] Run `. .venv312/Scripts/activate && PYTHONPATH=src python -m pytest tests -v` expecting all tests pass.
- [ ] If git repo is available, commit all changes with message `Improve translation speed and text rendering`.

## Self-Review

Spec coverage: OCR warm-up, translation cache, white-only rendering, bbox-derived font size all covered.
Placeholder scan: no placeholders.
Type consistency: `TranslatedBox.font_size` added before use in `main.py` and `overlay.py`.
