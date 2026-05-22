import subprocess
import sys


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "ViTrans",
        "--icon",
        "assets/logo.ico",
        "--add-data",
        "assets/logo.ico;assets",
        "--add-data",
        "assets/logo.png;assets",
        "--collect-all",
        "easyocr",
        "--collect-all",
        "torch",
        "--collect-all",
        "torchvision",
        "--paths",
        "src",
        "src/vitrans/main.py",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
