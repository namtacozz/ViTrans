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
        "--collect-data",
        "easyocr",
        "--collect-submodules",
        "easyocr",
        "--collect-submodules",
        "torchvision",
        "--hidden-import",
        "scipy._cyutility",
        "--paths",
        "src",
        "src/vitrans/main.py",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
