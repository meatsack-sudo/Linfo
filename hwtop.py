import sys
import os
import subprocess
import psutil
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QToolButton, QPushButton
from PyQt6.QtCore import QTimer, Qt
from sensors import sensor

class HWInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux HWInfo Prototype")
        self.setGeometry(100, 100, 800, 500)

        # Track expanded state for CPU frequency
        self.cpu_expanded = False

        # Check if running as root, if not restart with pkexec and preserve environment
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

        # Create an instance of our sensor class
        self.system_stats = sensor()

        # Main layout
        layout = QVBoxLayout()

        # Table for Min, Max, Avg, Current values
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Metric", "Min", "Max", "Avg", "Current"])
        layout.addWidget(self.table)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer for real-time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update every second

        # #Set default expansion arrow:
        # self.cpu_expansion_button.setArrowType(Qt.ArrowType.DownArrow)
    

    def toggle_cpu_expansion(self, checked):
        """
        Toggle expansion of CPU frequencies (per-core) on double-click 
        if the clicked row corresponds to "CPU Frequency".
        """
        self.cpu_expanded = checked
        self.update_stats()

    def update_stats(self):
       
        self.system_stats.update_all()

        # Separate metrics into base vs. per-core
        base_metrics = []
        per_core_keys = []
        for key in self.system_stats.stats:
            if key.startswith("Core "):
                per_core_keys.append(key)
            else:
                base_metrics.append(key)

        # Sort the per-core keys so they appear in numeric order: Core 0, Core 1, ...
        # per_core_keys.sort(key=lambda k: int(k.split()[1]))  # "Core 0 Frequency" -> 0

        # Decide how many rows we need. 
        # For example: all base metrics + per-core keys if expanded.
        base_count = len(base_metrics)
        core_count = len(per_core_keys) if self.cpu_expanded else 0
        total_rows = base_count + core_count
        self.table.setRowCount(total_rows)

        row = 0
        for key in base_metrics:
            # Grab the list of values for this metric
            values = self.system_stats.stats[key]
            if not values:
                continue

            # Special handling for CPU Frequency
            if key == "CPU Frequency":
                # Create arrow button
                cpu_expansion_arrow = QToolButton()
                cpu_expansion_arrow.setText("CPU Frequency")
                cpu_expansion_arrow.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                cpu_expansion_arrow.setCheckable(True)
                cpu_expansion_arrow.setChecked(self.cpu_expanded)
                cpu_expansion_arrow.toggled.connect(self.toggle_cpu_expansion)

                # Arrow direction
                if self.cpu_expanded:
                    cpu_expansion_arrow.setArrowType(Qt.ArrowType.UpArrow)
                else:
                    cpu_expansion_arrow.setArrowType(Qt.ArrowType.DownArrow)

                # Place the arrow button in column 0
                self.table.setCellWidget(row, 0, cpu_expansion_arrow)

                # Fill columns 1-4 with min, max, avg, current
                min_val = str(min(values))
                max_val = str(max(values))
                avg_val = str(int(sum(values) / len(values)))
                cur_val = str(values[-1])
                self.table.setItem(row, 1, QTableWidgetItem(min_val))
                self.table.setItem(row, 2, QTableWidgetItem(max_val))
                self.table.setItem(row, 3, QTableWidgetItem(avg_val))
                self.table.setItem(row, 4, QTableWidgetItem(cur_val))
                row += 1

                # If expanded, immediately insert per-core rows
                if self.cpu_expanded:
                    for core_key in per_core_keys:
                        core_values = self.system_stats.stats[core_key]
                        if not core_values:
                            continue
                        core_min = str(min(core_values))
                        core_max = str(max(core_values))
                        core_avg = str(int(sum(core_values) / len(core_values)))
                        core_cur = str(core_values[-1])

                        self.table.setItem(row, 0, QTableWidgetItem(core_key))
                        self.table.setItem(row, 1, QTableWidgetItem(core_min))
                        self.table.setItem(row, 2, QTableWidgetItem(core_max))
                        self.table.setItem(row, 3, QTableWidgetItem(core_avg))
                        self.table.setItem(row, 4, QTableWidgetItem(core_cur))
                        row += 1

            else:
                # For other base metrics
                min_val = str(min(values))
                max_val = str(max(values))
                avg_val = str(int(sum(values) / len(values)))
                cur_val = str(values[-1])

                self.table.setItem(row, 0, QTableWidgetItem(key))
                self.table.setItem(row, 1, QTableWidgetItem(min_val))
                self.table.setItem(row, 2, QTableWidgetItem(max_val))
                self.table.setItem(row, 3, QTableWidgetItem(avg_val))
                self.table.setItem(row, 4, QTableWidgetItem(cur_val))
                row += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HWInfoApp()
    window.show()
    sys.exit(app.exec())
