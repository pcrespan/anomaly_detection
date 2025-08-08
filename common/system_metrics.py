import psutil
import os

def get_system_metrics():
    return {
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "memory_percent": psutil.virtual_memory().percent,
        "load_avg": os.getloadavg()
    }