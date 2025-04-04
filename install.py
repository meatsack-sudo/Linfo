import os
import sys
import subprocess

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # Set by PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


APP_NAME = "linfo"
DESKTOP_ENTRY_NAME = f"{APP_NAME}.desktop"
DESKTOP_PATH = os.path.expanduser(f"~/.local/share/applications/{DESKTOP_ENTRY_NAME}")
ICON_PATH = resource_path("icon.svg")
EXECUTABLE_PATH = os.path.abspath(sys.argv[0])

DESKTOP_ENTRY_CONTENT = f"""[Desktop Entry]
Type=Application
Name=Hardware Top
Exec={EXECUTABLE_PATH}
Icon={ICON_PATH}
Terminal=false
Categories=Utility;
"""


def ensure_desktop_entry():
    if not os.path.exists(DESKTOP_PATH):
        print("Creating desktop entry...")
        os.makedirs(os.path.dirname(DESKTOP_PATH), exist_ok=True)
        with open(DESKTOP_PATH, "w") as f:
            f.write(DESKTOP_ENTRY_CONTENT)
        # Make it executable
        os.chmod(DESKTOP_PATH, 0o755)
        print(f"Desktop entry created at {DESKTOP_PATH}")
    else:
        print("Desktop entry already exists.")

def launch_hwtop():
    # Avoid recursion: this check ensures we don’t call ourselves infinitely
    if os.path.basename(sys.argv[0]) == "install.py":
        binary = os.path.join(os.path.dirname(EXECUTABLE_PATH), APP_NAME)
        subprocess.run([binary] + sys.argv[1:])
    else:
        from hwtop import LinfoApp
        from PyQt6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        window = LinfoApp()
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    ensure_desktop_entry()
    launch_hwtop()
