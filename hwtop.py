import sys
import psutil
import pyqtgraph as pg
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QProgressBar, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QTimer
import os

class HWInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux HWInfo Prototype")
        self.setGeometry(100, 100, 800, 500)

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
            "GPU Frequency": []
        }

        # Main layout
        layout = QVBoxLayout()

        # Table for Min, Max, Avg, Current values
        self.table = QTableWidget()
        self.table.setRowCount(len(self.stats))
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
            return int(psutil.cpu_freq().current)
        except:
            return "Unknown"

    def get_ram_frequency(self):
        try:
            output = subprocess.check_output(["dmidecode", "-t", "17"], text=True, stderr=subprocess.STDOUT)
            print("dmidecode output:\n", output)  # Debugging print statement
            frequencies = []
            for line in output.split("\n"):
                if "Configured Clock Speed:" in line or "Speed:" in line:
                    freq = line.split(":")[-1].strip().split(" ")[0]  # Extract MHz value
                    if freq.isdigit():
                        frequencies.append(int(freq))
            if frequencies:
                return max(frequencies)  # Return highest detected frequency
            print("No valid RAM frequency found in dmidecode output.")
        except subprocess.CalledProcessError as e:
            print(f"dmidecode failed: {e.output}")
        except FileNotFoundError:
            print("dmidecode command not found.")

        # Fallback to lshw if dmidecode fails
        try:
            output = subprocess.check_output(["lshw", "-C", "memory"], text=True, stderr=subprocess.STDOUT)
            print("lshw output:\n", output)  # Debugging print statement
            for line in output.split("\n"):
                if "clock:" in line:
                    return int(line.split(":")[-1].strip().split(" ")[0])
            print("No valid RAM frequency found in lshw output.")
        except subprocess.CalledProcessError as e:
            print(f"lshw failed: {e.output}")
        except FileNotFoundError:
            print("lshw command not found.")

        return "Unknown"

    def get_gpu_frequency(self):
        try:
            output = subprocess.check_output(["nvidia-smi", "--query-gpu=clocks.gr", "--format=csv,noheader"], text=True)
            return int(output.strip().split(" ")[0])  # Extract MHz value
        except:
            return "Unknown"

    def update_stats(self):
        # Update statistics
        cpu_usage = self.update_stat("CPU Usage", psutil.cpu_percent())
        cpu_freq = self.update_stat("CPU Frequency", self.get_cpu_frequency())
        ram_usage = self.update_stat("RAM Usage", psutil.virtual_memory().percent)
        ram_freq = self.update_stat("RAM Frequency", self.get_ram_frequency())
        gpu_freq = self.update_stat("GPU Frequency", self.get_gpu_frequency())

        # Update table values
        for i, (key, values) in enumerate(self.stats.items()):
            if values:
                self.table.setItem(i, 0, QTableWidgetItem(key))
                self.table.setItem(i, 1, QTableWidgetItem(str(min(values))))
                self.table.setItem(i, 2, QTableWidgetItem(str(max(values))))
                self.table.setItem(i, 3, QTableWidgetItem(str(int(sum(values) / len(values)))))
                self.table.setItem(i, 4, QTableWidgetItem(str(values[-1])))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HWInfoApp()
    window.show()
    sys.exit(app.exec())