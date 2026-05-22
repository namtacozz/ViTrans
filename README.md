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

First OCR run may download EasyOCR models. After startup, ViTrans warms OCR in the background to reduce first translation delay.

## Use

- Press `Alt+T` to open full-screen selection mode.
- Click and drag from one corner of the desired area to the opposite corner.
- Release mouse to create the overlay on that rectangle.
- Press `Alt+T` again while overlay is visible to hide it.
- Put overlay around text in another app.
- Click `ViTrans`.
- Translated Vietnamese text appears as white text over detected text, sized from OCR line boxes.
- Click `X` to hide overlay.
- Use tray menu `Exit` to exit.
- Right-click tray icon for `Open Ui` and `Exit`.

## Test

```bash
. .venv312/Scripts/activate
PYTHONPATH=src python -m pytest tests -v
```

## Manual validation checklist

- `Alt+T` opens full-screen selection mode.
- Dragging selection rectangle previews selected area.
- Releasing mouse creates overlay on selected rectangle.
- Pressing `Alt+T` while overlay is visible hides it.
- Tray icon appears in the right side of the Windows taskbar.
- Right-click tray menu shows `Open Ui` and `Exit`.
- Overlay stays above other apps.
- `X` hides overlay while app stays in tray.
- Capture works over another app.
- English text inside overlay is OCR'd and translated to Vietnamese.
- Translation appears near original text positions with readable background blocks.
- Network translation failure shows an error instead of crashing.
