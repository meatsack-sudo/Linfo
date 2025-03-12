import sys
import os
import subprocess
import psutil
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
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
        self.table.cellDoubleClicked.connect(self.toggle_cpu_expansion)
        layout.addWidget(self.table)

        # Set central widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timer for real-time updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Update every second

    def toggle_cpu_expansion(self, row, column):
        """
        Toggle expansion of CPU frequencies (per-core) on double-click 
        if the clicked row corresponds to "CPU Frequency".
        """
        item = self.table.item(row, 0)
        if item and item.text() == "CPU Frequency":
            self.cpu_expanded = not self.cpu_expanded  # Toggle expansion state
            self.update_stats()

    def update_stats(self):
        """
        Called periodically by the timer. Fetch latest sensor data and 
        update the table rows accordingly.
        """
        # Update all stats, capture per-core frequencies
        per_core_freqs = self.system_stats.update_all()

        # Prepare the table rows
        # If CPU is expanded, we need extra rows for each core
        total_rows = len(self.system_stats.stats) + (len(per_core_freqs) if self.cpu_expanded else 0)
        self.table.setRowCount(total_rows)

        row = 0
        for key, values in self.system_stats.stats.items():
            # If CPU Frequency is expanded, insert per-core rows
            if key == "CPU Frequency" and self.cpu_expanded and len(per_core_freqs) > 0:
                for core_index, freq in enumerate(per_core_freqs):
                    self.table.setItem(row, 0, QTableWidgetItem(f"Core {core_index}"))
                    self.table.setItem(row, 1, QTableWidgetItem(str(freq)))
                    self.table.setItem(row, 2, QTableWidgetItem(str(freq)))
                    self.table.setItem(row, 3, QTableWidgetItem(str(freq)))
                    self.table.setItem(row, 4, QTableWidgetItem(str(freq)))
                    row += 1
            else:
                # For standard metrics, fill out min, max, avg, current
                if values:  # Make sure there's at least one data point
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
