import sys
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QCursor, QGuiApplication, QAction


def is_wayland():
    return QGuiApplication.platformName().lower() == "wayland"

# ---------------------------------------------
# QSystemTrayIcon version (for X11)
# ---------------------------------------------
class QtTray:
    def __init__(self, parent, icon_path):
        self.parent = parent
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), parent)
        self.tray_icon.setToolTip("Linfo running in tray")

        self.menu = QMenu()
        self.restore_action = QAction("Restore Window", parent)
        self.restore_action.triggered.connect(parent.restore_from_tray)
        self.menu.addAction(self.restore_action)

        self.quit_action = QAction("Quit", parent)
        self.quit_action.triggered.connect(parent.quit_app)
        self.menu.addAction(self.quit_action)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self.on_activated)
        self.tray_icon.show()

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.parent.restore_from_tray()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            self.menu.exec(QCursor.pos())

# ---------------------------------------------
# Ayatana AppIndicator version (for Wayland)
# ---------------------------------------------
class AyatanaTray:
    def __init__(self, parent, icon_path):
        import gi
        gi.require_version('Gtk', '3.0')
        gi.require_version('AyatanaAppIndicator3', '0.1')
        from gi.repository import Gtk, AyatanaAppIndicator3 as AppIndicator
        from threading import Thread

        self.parent = parent

        self.indicator = AppIndicator.Indicator.new(
            "linfo-indicator",
            icon_path,
            AppIndicator.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator.IndicatorStatus.ACTIVE)

        self.menu = Gtk.Menu()

        item_restore = Gtk.MenuItem(label='Restore Window')
        item_restore.connect('activate', lambda _: parent.restore_from_tray())
        self.menu.append(item_restore)

        item_quit = Gtk.MenuItem(label='Quit')
        item_quit.connect('activate', lambda _: parent.quit_app())
        self.menu.append(item_quit)

        self.menu.show_all()
        self.indicator.set_menu(self.menu)

        # Run GTK main loop in the background
        Thread(target=Gtk.main, daemon=True).start()

# ---------------------------------------------
# Public helper
# ---------------------------------------------
def create_tray(parent, icon_path):
    if is_wayland():
        print("Wayland detected — using AyatanaAppIndicator")
        return AyatanaTray(parent, icon_path)
    else:
        print("X11 detected — using QSystemTrayIcon")
        return QtTray(parent, icon_path)
