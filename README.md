# ViTrans

Vit Translate App.

Windows Python MVP for translating text inside a screen overlay.

## Setup

Use Python 3.12. EasyOCR/PyTorch may fail on Python 3.14.

```bash
py -3.12 -m venv .venv312
. .venv312/Scripts/activate
pip install -r requirements.txt
```

## Run

```bash
. .venv312/Scripts/activate
PYTHONPATH=src python -m vitrans.main
```

First OCR run may download EasyOCR models. ViTrans shows its UI first, then warms OCR in the background after startup to reduce first translation delay.

## Use

- Press `Alt+T` (default hotkey, configurable) to open full-screen selection mode.
- Click and drag from one corner of the desired area to the opposite corner.
- Release mouse to create a translucent overlay box on that rectangle. Boxes can be as small as a single word selection.
- Click the app icon in the center of the box to translate; the icon hides after translation.
- Press `Alt+T` again to create another overlay box without closing existing boxes, even while another box is translating.
- Move or resize a box to clear its translation and show the center icon again.
- Right-click a box to choose source language, target language, or close only that box.
- OCR runs one box at a time to keep EasyOCR stable; translation continues without blocking new selections.
- Translated text appears as white text over detected text, sized from OCR line boxes.
- **Double-click tray icon** to open Settings window.

### Settings Window

Double-click the tray icon to open the EVKey-style settings dialog:

- **Dịch thuật**: Choose source language (auto-detect, English, Vietnamese, Japanese, Korean, Chinese, French, German) and target language.
- **Cơ bản**: Change overlay color (Blue, Green, Red, Purple, Orange, White) and customize the global hotkey (modifier + key).
- **Hệ thống**: Run with admin privileges, auto-start with Windows.
- Click **Lưu** to save changes. Click **Đặt lại** to reset to defaults.
- **Thoát** exits the application. Closing the settings window with `X` hides it to tray.

## Build Windows app

```bash
. .venv312/Scripts/activate
python scripts/build_windows.py
./dist/ViTrans/ViTrans.exe
```

Build output is a one-folder Windows app at `dist/ViTrans/`. Running `ViTrans.exe` gives Windows a real process name and icon for Task Manager and taskbar/tray behavior.

## Test

```bash
. .venv312/Scripts/activate
PYTHONPATH=src python -m pytest tests -v
```

## Manual validation checklist

- `Alt+T` opens full-screen selection mode.
- Dragging selection rectangle previews selected area.
- Releasing mouse creates a translucent overlay box on selected rectangle, including small one-word selections.
- Center app icon starts OCR/translation and hides after translation.
- Pressing `Alt+T` again creates a second overlay box without closing the first, even while another box is translating.
- Right-clicking an overlay box shows source language, target language, and close actions.
- Closing one overlay box does not close other boxes.
- Moving or resizing a box clears translated text and shows the center icon again.
- Tray icon appears in the right side of the Windows taskbar.
- **Double-clicking tray icon opens the Settings window.**
- Settings window shows three groups: Dịch thuật, Cơ bản, Hệ thống, without a duplicate custom logo/version header.
- Changing overlay color and saving updates all visible overlay rectangle colors.
- Changing hotkey and saving updates the global shortcut without restart.
- Overlay boxes stay above other apps.
- Capture works over another app.
- Text inside overlay is OCR'd and translated to the configured target language.
- Translation appears near original text positions with readable background blocks.
- Network translation failure shows an error instead of crashing.
