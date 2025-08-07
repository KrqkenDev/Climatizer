import psutil
import os
import time
import platform

try:
    import wmi  # Windows Compatibility (broken for temperature readings for now)
except ImportError:
    wmi = None

def get_stats():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage('/').percent
    temps = {}

    system = platform.system()

    if system in ["Linux", "Darwin"]:
        if hasattr(psutil, "sensors_temperatures"):
            raw = psutil.sensors_temperatures()
            if raw:
                for name, entries in raw.items():
                    for entry in entries:
                        label = entry.label or f"{name} Core"
                        temps[label] = entry.current
            else:
                print("No temperature data found.")
        else:
            print("Temperature monitoring not supported on this platform.")

    elif system == "Windows":
        if wmi:
            try:
                w = wmi.WMI(namespace="root\\wmi")
                for i, sensor in enumerate(w.MSAcpi_ThermalZoneTemperature()):
                    temp_c = (sensor.CurrentTemperature / 10.0) - 273.15
                    label = sensor.InstanceName or f"Sensor{i}"
                    temps[label] = round(temp_c, 1)
            except Exception as e:
                print(f"WMI temp read failed: {e}")
        else:
            print("WMI not available. Run 'pip install wmi'.")

    return cpu, mem, disk, temps


def log_stats():
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    cpu, mem, disk, temps = get_stats()

    log_line = f"{now} - CPU: {cpu}%, CPU Temps: {temps}, Memory: {mem}%, Disk: {disk}%\n"

    with open("system_stats.log", "a") as f:
        f.write(log_line)

    print(log_line.strip())
    print(f"Logged at {now}")


if __name__ == "__main__":
    if not os.path.exists("system_stats.log"):
        with open("system_stats.log", "w") as f:
            f.write("System Stats Log\n")
            f.write("Time - CPU - Temps - Memory - Disk\n")

    while True:
        log_stats()
        time.sleep(1)
