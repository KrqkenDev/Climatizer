import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import re
from datetime import datetime, timedelta

LOG_FILE = "system_stats.log"

#Parse logs

pattern = re.compile(
    r"(?P<time>[\d\-:\s]+)\s-\sCPU:\s(?P<cpu>[\d.]+)%,\sCPU Temps:\s(?P<temps>\{.*?\}),\sMemory:\s(?P<memory>[\d.]+)%,\sDisk:\s(?P<disk>[\d.]+)%"
)

def parse_log():
    rows = []
    with open(LOG_FILE, "r") as f:
        for line in f:
            m = pattern.search(line)
            if m:
                try:
                    time = datetime.strptime(m.group("time"), "%Y-%m-%d %H:%M:%S")
                    cpu = float(m.group("cpu"))
                    memory = float(m.group("memory"))
                    disk = float(m.group("disk"))
                    temps = eval(m.group("temps")) if m.group("temps") else {}
                    rows.append({"Time": time, "CPU": cpu, "Memory": memory, "Disk": disk, **temps})
                except Exception:
                    pass
    return pd.DataFrame(rows)

# Set up the figure
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Live System Stats")

def animate(i):
    df = parse_log()
    if df.empty:
        return

    recent = df[df["Time"] >= datetime.now() - timedelta(minutes=2)]
    times = recent["Time"]

    axs[0, 0].clear()
    axs[0, 0].plot(times, recent["CPU"], color="red")
    axs[0, 0].set_title("CPU Usage (%)")

    axs[0, 1].clear()
    axs[0, 1].plot(times, recent["Memory"], color="blue")
    axs[0, 1].set_title("Memory Usage (%)")

    axs[1, 0].clear()
    axs[1, 0].plot(times, recent["Disk"], color="green")
    axs[1, 0].set_title("Disk Usage (%)")

    axs[1, 1].clear()
    temp_keys = [col for col in recent.columns if col not in ["Time", "CPU", "Memory", "Disk"]]
    for key in temp_keys:
        axs[1, 1].plot(times, recent[key], label=key)
    axs[1, 1].set_title("CPU Temps")
    axs[1, 1].legend()

    for ax in axs.flat:
        ax.set_xlabel("Time")
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True)

ani = animation.FuncAnimation(fig, animate, interval=5000)
plt.tight_layout()
plt.show()
