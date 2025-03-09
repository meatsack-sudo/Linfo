import sys
import psutil
import pyqtgraph as pg
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QTimer, Qt
import os

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

        # Initialize statistics tracking
        self.stats = {
            "CPU Usage": [],
            "CPU Frequency": [],
            "RAM Usage": [],
            "RAM Frequency": [],
            "GPU Frequency": [],
            "GPU Power (Watts)": [],
        }

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

    def update_stat(self, key, value):
        if value == "Unknown" or value is None:
            return "Unknown"
        
        try:
            value = float(value)
            self.stats[key].append(value)
            if len(self.stats[key]) > 50:  # Limit stored values
                self.stats[key].pop(0)
            return value
        except ValueError:
            return "Unknown"

    def get_cpu_frequency(self):
        try:
            overall_freq = int(psutil.cpu_freq().current)
            per_core_freqs = [f.current for f in psutil.cpu_freq(percpu=True)]
            return overall_freq, per_core_freqs
        except:
            return "Unknown", []

    def get_ram_frequency(self):
        try:
            output = subprocess.check_output(["dmidecode", "-t", "17"], text=True, stderr=subprocess.STDOUT)
            frequencies = []
            for line in output.split("\n"):
                if "Configured Clock Speed:" in line or "Speed:" in line:
                    freq = line.split(":")[-1].strip().split(" ")[0]  # Extract MHz value
                    if freq.isdigit():
                        frequencies.append(int(freq))
            if frequencies:
                return max(frequencies)  # Return highest detected frequency
        except:
            return "Unknown"

        return "Unknown"

    def get_gpu_frequency(self):
        try:
            output = subprocess.check_output(["nvidia-smi", "--query-gpu=clocks.gr", "--format=csv,noheader"], text=True)
            return int(output.strip().split(" ")[0])  # Extract MHz value
        except:
            return "Unknown"
        
    def get_gpu_power(self):
        try:
            output = subprocess.check_output(["nvidia-smi", "--query-gpu=gpu.power.draw.instant", "--format=csv,noheader,nounits"], text=True)
            return int(float(output.strip()))
 # Extract total wattage of GPU +/- 5 watts
        except:
            return "Unknown"

    def toggle_cpu_expansion(self, row, column):
        item = self.table.item(row, 0)
        if item and item.text() == "CPU Frequency":
            self.cpu_expanded = not self.cpu_expanded  # Toggle expansion state
            self.update_stats()

    def update_stats(self):
        # Update statistics
        cpu_usage = self.update_stat("CPU Usage", psutil.cpu_percent())
        cpu_freq, per_core_freqs = self.get_cpu_frequency()
        overall_cpu_freq = self.update_stat("CPU Frequency", cpu_freq)
        ram_usage = self.update_stat("RAM Usage", psutil.virtual_memory().percent)
        ram_freq = self.update_stat("RAM Frequency", self.get_ram_frequency())
        gpu_freq = self.update_stat("GPU Frequency", self.get_gpu_frequency())
        gpu_power = self.update_stat("GPU Power (Watts)", self.get_gpu_power())


        # Prepare table
        total_rows = len(self.stats) + (len(per_core_freqs) if self.cpu_expanded else 0)
        self.table.setRowCount(total_rows)
        row = 0

        for key, values in self.stats.items():
            if key == "CPU Frequency" and self.cpu_expanded:
                # Insert per-core frequencies
                for core_index, freq in enumerate(per_core_freqs):
                    self.table.setItem(row, 0, QTableWidgetItem(f"Core {core_index}"))
                    self.table.setItem(row, 1, QTableWidgetItem(str(freq)))
                    self.table.setItem(row, 2, QTableWidgetItem(str(freq)))
                    self.table.setItem(row, 3, QTableWidgetItem(str(freq)))
                    self.table.setItem(row, 4, QTableWidgetItem(str(freq)))
                    row += 1
            else:
                if values:
                    self.table.setItem(row, 0, QTableWidgetItem(key))
                    self.table.setItem(row, 1, QTableWidgetItem(str(min(values))))
                    self.table.setItem(row, 2, QTableWidgetItem(str(max(values))))
                    self.table.setItem(row, 3, QTableWidgetItem(str(int(sum(values) / len(values)))))
                    self.table.setItem(row, 4, QTableWidgetItem(str(values[-1])))
                    row += 1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HWInfoApp()
    window.show()
    sys.exit(app.exec())
