# settings_window.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QIcon
from install import resource_path

class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setWindowIcon(QIcon(resource_path("icon.svg")))
        self.setFixedSize(300, 200)
        layout = QVBoxLayout()

        self.settings = QSettings("Linfo", "LinfoApp")

        # Start Minimized Option
        self.start_minimized_cb = QCheckBox("Start minimized to tray")
        self.start_minimized_cb.setChecked(self.settings.value("start_minimized", False, type=bool))
        layout.addWidget(self.start_minimized_cb)

        # Per-core expansion
        self.cpu_expanded_cb = QCheckBox("Show per-core CPU frequency by default")
        self.cpu_expanded_cb.setChecked(self.settings.value("cpu_expanded", False, type=bool))
        layout.addWidget(self.cpu_expanded_cb)

        # Polling interval
        layout.addWidget(QLabel("Polling Interval (ms):"))
        self.polling_combo = QComboBox()
        self.polling_combo.addItems(["500", "1000", "2000"])
        current = str(self.settings.value("polling_interval", 1000, type=int))
        self.polling_combo.setCurrentText(current)
        layout.addWidget(self.polling_combo)

        # Theme selection dropdown
        layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        current_theme = self.settings.value("theme", "dark")
        self.theme_combo.setCurrentText(current_theme)
        layout.addWidget(self.theme_combo)

        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save_settings(self):
        self.settings.setValue("start_minimized", self.start_minimized_cb.isChecked())
        self.settings.setValue("cpu_expanded", self.cpu_expanded_cb.isChecked())
        self.settings.setValue("polling_interval", int(self.polling_combo.currentText()))
        self.settings.setValue("theme", self.theme_combo.currentText())

        self.close()
