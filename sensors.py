import psutil
import subprocess
import platform


class sensor:
# Main class for fetching and tracking our stats
    def __init__(self):
        self.stats = {
            "CPU Usage": [],
            "CPU Frequency": [],
            "CPU Temperature": [],
            "GPU Temperature": [],
            "RAM Usage": [],
            "RAM Frequency": [],
            "GPU Frequency": [],
            "GPU Power": [],
        }

        self.units = {
            "CPU Usage": "%",
            "CPU Frequency": "MHz",
            "CPU Temperature": "°C",
            "GPU Temperature": "°C",
            "RAM Usage": "%",
            "RAM Frequency": "MHz",
            "GPU Frequency": "MHz",
            "GPU Power": "W",
        }

        self.component_names = {
            "CPU": self.get_cpu_name(),
            "GPU": self.get_gpu_name(),
}


    def update_stats(self, key, value):
        if value == "Unknown" or value is None:
            return "Unknown"
        
        try:
            value = float(value)
            if key not in self.stats:
                self.stats[key] = []            
            self.stats[key].append(value)
            
            # When the list exceeds 50 values, try to preserve the min and max
            if len(self.stats[key]) > 50:
                current_min = min(self.stats[key])
                current_max = max(self.stats[key])
                
                removed = False
                # Try to remove the first element that isn't the min or max
                for i in range(len(self.stats[key])):
                    if self.stats[key][i] != current_min and self.stats[key][i] != current_max:
                        self.stats[key].pop(i)
                        removed = True
                        break
                        
                # if every element is min or max, remove the first one
                if not removed:
                    self.stats[key].pop(0)
                    
            return value
        except ValueError:
            return "Unknown"
        
    def get_cpu_name(self):
        try:
            return subprocess.check_output(["lscpu"], text=True).split("Model name:")[1].strip().split("\n")[0]
        except:
            return platform.processor()

    def get_gpu_name(self):
        try:
            output = subprocess.check_output(["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"], text=True)
            return output.strip()
        except:
            return "Unknown GPU"

        
    def get_cpu_frequency(self):
        """
        Return a tuple of (overall CPU frequency [MHz], list of per-core freq).
        """
        try:
            overall_freq = int(psutil.cpu_freq().current)
            per_core_freqs = [f.current for f in psutil.cpu_freq(percpu=True)]
            return overall_freq, per_core_freqs
        except:
            return "Unknown", []
        
    def get_cpu_temperature(self):
        """
        Return CPU temperature via psutil
        """
        try:
            temps = psutil.sensors_temperatures()

            if not temps:
                return "Unknown"

            # Common label on Intel systems is "coretemp".
            # AMD might be "k10temp", need to verify.
            for name, entries in temps.items():
                # If you see 'coretemp' or 'k10temp' or something else in `temps.keys()`
                if name.lower() in ["coretemp", "k10temp", "cpu-thermal"]:
                    # Gather all core temperatures; you can average them
                    core_readings = [temp.current for temp in entries if temp.current is not None]
                    if core_readings:
                        return sum(core_readings) / len(core_readings)
            return "Unknown"
        except Exception:
            return "Unknown"
        
    def get_ram_frequency(self):
        """
        Try to read RAM frequency from 'dmidecode -t 17'. 
        Returns the highest detected frequency or 'Unknown'.
        """
        try:
            output = subprocess.check_output([
                "pkexec", "dmidecode", "-t", "17"
            ], text=True, stderr=subprocess.STDOUT)
            frequencies = []
            for line in output.split("\n"):
                if "Configured Clock Speed:" in line or "Speed:" in line:
                    freq = line.split(":")[-1].strip().split(" ")[0]  # Extract MHz value
                    if freq.isdigit():
                        frequencies.append(int(freq))
            if frequencies:
                return max(frequencies)
        except:
            pass
        return "Unknown"

    def get_gpu_frequency(self):
        """
        Uses nvidia-smi to read GPU frequency (MHz).
        Returns int or 'Unknown'.
        """
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=clocks.gr", "--format=csv,noheader"],
                text=True
            )
            return int(output.strip().split(" ")[0])  # e.g. "1500 MHz" -> 1500
        except:
            return "Unknown"

    def get_gpu_power(self):
        """
        Uses nvidia-smi to read GPU power (Watts).
        Returns int or 'Unknown'.
        """
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=gpu.power.draw.instant", "--format=csv,noheader,nounits"],
                text=True
            )
            return int(float(output.strip()))
        except:
            return "Unknown"
        
    def get_gpu_temperature(self):
        """
        Uses nvidia-smi to read the GPU temperature. For AMD GPUs or Intel iGPUs,
        we'll need to re-evaluate.
        """
        try:
            output = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader"],
                text=True
            )
            return float(output.strip())
        except Exception:
            return "Unknown"

    def update_all(self):
        """
        Fetch the latest values for each metric and update self.stats.
        Returns a dict of (key -> last_value).
        """
        # CPU Usage
        cpu_usage = self.update_stats("CPU Usage", psutil.cpu_percent())

        # CPU Frequency
        cpu_freq, per_core_freqs = self.get_cpu_frequency()
        self.update_stats("CPU Frequency", cpu_freq)

        # Update per-core frequency history:
        for i, freq in enumerate(per_core_freqs):
            self.update_stats(f"Core {i} Frequency", freq)

        # CPU Temperature
        self.update_stats("CPU Temperature", self.get_cpu_temperature())

        # RAM Usage
        self.update_stats("RAM Usage", psutil.virtual_memory().percent)

        # RAM Frequency
        self.update_stats("RAM Frequency", self.get_ram_frequency())

        # GPU Frequency
        self.update_stats("GPU Frequency", self.get_gpu_frequency())

        # GPU Power
        self.update_stats("GPU Power", self.get_gpu_power())

        #GPU Temperature
        self.update_stats("GPU Temperature", self.get_gpu_temperature())
        
        # Return the tuple or list of per-core frequencies if needed by the GUI
        return per_core_freqs