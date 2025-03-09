import psutil



def get_per_cpu_frequency():
    try: 
        return psutil.cpu_freq(percpu=True)
    except: return "Unknown"


print(get_per_cpu_frequency())