import sys
import os
import subprocess
import psutil
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QToolButton
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QFont
from sensors import sensor

class HWInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux HWInfo Prototype")
        self.setGeometry(100, 100, 800, 500)

        # Used to toggle per-core frequency display
        self.cpu_expanded = False

        # Request root access if not already root
        if os.geteuid() != 0:
            print("Requesting root access via pkexec...")
            user_python = subprocess.check_output("which python3", shell=True, text=True).strip()
            env_vars = {
                "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
                "DISPLAY": os.environ.get("DISPLAY", ""),
                "XAUTHORITY": os.environ.get("XAUTHORITY", ""),
                "PATH": os.environ.get("PATH", "")
            }
            os.execvpe("pkexec", ["pkexec", user_python] + sys.argv, env_vars)

        # Initialize hardware sensor backend
        self.system_stats = sensor()

        # Set up main layout
        layout = QVBoxLayout()

        # Create table widget for stat display
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setColumnWidth(0, 200)
        self.table.setHorizontalHeaderLabels(["Metric", "Min", "Max", "Avg", "Current"])
        layout.addWidget(self.table)

        # Embed layout into main window
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Set timer for regular stat updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)

    def toggle_cpu_expansion(self, checked):
        # Callback for expanding/collapsing per-core frequency rows
        self.cpu_expanded = checked
        self.update_stats()

    def get_unit_for_key(self, key):
        # Returns the unit string for a given stat key
        if key.startswith("Core "):
            return "MHz"
        return self.system_stats.units.get(key, "")

    def get_colored_item(self, key, value, unit):
        # Returns a table item with unit, bold font, color-coded if needed
        text = f"{value} {unit}"
        item = QTableWidgetItem(text)

        # Bold font for current values
        font = QFont()
        font.setBold(True)
        item.setFont(font)

        # Align to the right and center vertically
        item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        # Threshold-based color coding
        if key == "CPU Temperature" and isinstance(value, (int, float)):
            if value > 80:
                item.setForeground(QColor("red"))
            elif value > 60:
                item.setForeground(QColor("orange"))

        elif key == "GPU Temperature" and isinstance(value, (int, float)):
            if value > 85:
                item.setForeground(QColor("red"))
            elif value > 70:
                item.setForeground(QColor("orange"))

        elif key == "CPU Usage" and isinstance(value, (int, float)):
            if value > 90:
                item.setForeground(QColor("red"))
            elif value > 70:
                item.setForeground(QColor("orange"))

        elif key == "GPU Power" and isinstance(value, (int, float)):
            if value > 110:
                item.setForeground(QColor("red"))
            elif value > 90:
                item.setForeground(QColor("orange"))

        return item

    def update_stats(self):
        # Trigger data refresh and update the table
        self.system_stats.update_all()

        # Split metrics into base and per-core frequency rows
        base_metrics = []
        per_core_keys = []
        for key in self.system_stats.stats:
            if key.startswith("Core "):
                per_core_keys.append(key)
            else:
                base_metrics.append(key)

        # Determine total number of rows needed
        base_count = len(base_metrics)
        core_count = len(per_core_keys) if self.cpu_expanded else 0
        total_rows = base_count + core_count
        self.table.setRowCount(total_rows)

        row = 0
        for key in base_metrics:
            values = self.system_stats.stats[key]
            if not values:
                continue

            unit = self.get_unit_for_key(key)

            # CPU Frequency gets a toggle button for expansion
            if key == "CPU Frequency":
                cpu_expansion_arrow = QToolButton()
                cpu_expansion_arrow.setText("CPU Frequency")
                cpu_expansion_arrow.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                cpu_expansion_arrow.setCheckable(True)
                cpu_expansion_arrow.setChecked(self.cpu_expanded)
                cpu_expansion_arrow.toggled.connect(self.toggle_cpu_expansion)
                cpu_expansion_arrow.setArrowType(Qt.ArrowType.UpArrow if self.cpu_expanded else Qt.ArrowType.DownArrow)
                self.table.setCellWidget(row, 0, cpu_expansion_arrow)

                # Min, Max, Avg values (no coloring needed)
                for col, val in zip(range(1, 4), [min(values), max(values), int(sum(values) / len(values))]):
                    item = QTableWidgetItem(f"{val} {unit}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(row, col, item)

                # Current value with styling
                self.table.setItem(row, 4, self.get_colored_item(key, values[-1], unit))
                row += 1

                # If expanded, show all core frequencies
                if self.cpu_expanded:
                    for core_key in sorted(per_core_keys, key=lambda k: int(k.split()[1])):
                        core_values = self.system_stats.stats[core_key]
                        if not core_values:
                            continue
                        unit = self.get_unit_for_key(core_key)

                        self.table.setItem(row, 0, QTableWidgetItem(core_key))
                        for col, val in zip(range(1, 4), [min(core_values), max(core_values), int(sum(core_values) / len(core_values))]):
                            item = QTableWidgetItem(f"{val} {unit}")
                            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                            self.table.setItem(row, col, item)
                        self.table.setItem(row, 4, self.get_colored_item(core_key, core_values[-1], unit))
                        row += 1
            else:
                # Normal metric row
                self.table.setItem(row, 0, QTableWidgetItem(key))
                for col, val in zip(range(1, 4), [min(values), max(values), int(sum(values) / len(values))]):
                    item = QTableWidgetItem(f"{val} {unit}")
                    item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.table.setItem(row, col, item)
                self.table.setItem(row, 4, self.get_colored_item(key, values[-1], unit))
                row += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HWInfoApp()
    window.show()
    sys.exit(app.exec())
