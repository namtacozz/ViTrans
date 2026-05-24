# ViTrans project context

ViTrans is a Windows desktop overlay translator. It uses PyQt6 for UI, EasyOCR for local OCR, deep-translator for Google Translate, pynput for global hotkeys, and PyInstaller for Windows packaging.

## Commands

Use Python 3.12 environment `.venv312`; `.venv` may point to Python 3.14 and cannot install pinned `torch==2.5.1`.

```bash
PYTHONPATH=src ./.venv312/Scripts/python.exe -m pytest -q
./.venv312/Scripts/python.exe scripts/build_windows.py
./dist/ViTrans/ViTrans.exe
```

## Current behavior

- Double-click tray icon opens Settings.
- Right-click tray icon is intentionally unused.
- `Alt+T` opens selection mode and creates a new overlay box; existing boxes stay visible.
- Each overlay box has a center app icon. Clicking it translates that box and hides the icon.
- Moving or resizing a box clears its translation and shows the icon again.
- Right-click an overlay box to choose source language, target language, or close only that box.
- OCR should run one job at a time; translation can run outside the OCR lock.

## Build notes

Build output lives at `dist/ViTrans/ViTrans.exe`. PyInstaller warnings about optional TensorBoard or SciPy hidden imports may appear; verify runtime behavior before changing dependency pins.
