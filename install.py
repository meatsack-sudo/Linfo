#!/usr/bin/env python3
import subprocess
import sys
import os


def resource_path(relative_path):
    # Always resolve relative to the install.py location
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)



APP_NAME = "linfo"
DESKTOP_ENTRY_NAME = f"{APP_NAME}.desktop"
LOCAL_APPS_PATH = os.path.expanduser("~/.local/share/applications")
ICON_TARGET_PATH = os.path.expanduser(f"~/.local/share/icons/{APP_NAME}.svg")
EXECUTABLE_PATH = os.path.abspath("hwtop.py")  # <- change to hwtop

def ensure_icon():
    source_icon = resource_path("icon.svg")
    if os.path.exists(source_icon):
        os.makedirs(os.path.dirname(ICON_TARGET_PATH), exist_ok=True)
        with open(source_icon, "rb") as src, open(ICON_TARGET_PATH, "wb") as dst:
            dst.write(src.read())
        print(f"Copied icon to {ICON_TARGET_PATH}")
    else:
        print("Warning: icon.svg not found. Icon will not appear in launcher.")

DESKTOP_ENTRY_CONTENT = f"""[Desktop Entry]
Type=Application
Name=Linfo
Comment=Linux Hardware Monitor
Comment[en_US]=Linux Hardware Monitor
Exec=bash -c "python3 {EXECUTABLE_PATH}"
Icon={ICON_TARGET_PATH}
Terminal=false
Categories=Utility;
"""

def ensure_requirements():
    if os.path.exists("requirements.txt"):
        print("Installing requirements from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    else:
        print("No requirements.txt found, skipping dependency install.")

def ensure_desktop_entry():
    desktop_path = os.path.join(LOCAL_APPS_PATH, DESKTOP_ENTRY_NAME)
    if not os.path.exists(desktop_path):
        print("Creating desktop entry...")
        os.makedirs(LOCAL_APPS_PATH, exist_ok=True)
        with open(desktop_path, "w") as f:
            f.write(DESKTOP_ENTRY_CONTENT)
        os.chmod(desktop_path, 0o755)
        print(f"Desktop entry created at {desktop_path}")
    else:
        print("Desktop entry already exists.")

def launch_linfo():
    from hwtop import LinfoApp
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = LinfoApp()
    window.show()
    sys.exit(app.exec())

def ensure_executables():
    paths_to_fix = [
        os.path.abspath("hwtop.py"),
        os.path.abspath("linfo_launcher.sh"),
        os.path.abspath(__file__),  # Optional: make install.py executable too
    ]

    for path in paths_to_fix:
        if os.path.exists(path):
            current_mode = os.stat(path).st_mode
            os.chmod(path, current_mode | 0o111)
            print(f"Made {path} executable.")
        else:
            print(f"Warning: {path} not found.")



if __name__ == "__main__":
    ensure_executables()
    ensure_icon()
    ensure_desktop_entry()
    ensure_requirements()
    launch_linfo()

