import tkinter as tk
from tkinter import Canvas
import pandas as pd
import re
import math
import json
from datetime import datetime

# --------------------------
# Configuration
# --------------------------

# Default settings
settings = {
    "metrics": {"CPU": True, "Memory": True, "Disk": True, "Temp": True},
    "colors": {"bg": "#000000", "fg": "#FFFFFF"}
}


try:
    with open("settings.json") as f:
        settings.update(json.load(f))
except Exception:
    pass  # Use default settings if file missing or invalid

BG_COLOR = settings["colors"]["bg"]
FG_COLOR = settings["colors"]["fg"]
LOG_FILE = "system_stats.log"

# --------------------------
# Log Parsing
# --------------------------

log_pattern = re.compile(
    r"(?P<time>[\d\-:\s]+)\s-\sCPU:\s(?P<cpu>[\d.]+)%,\sCPU Temps:\s(?P<temps>\{.*?\}),\sMemory:\s(?P<memory>[\d.]+)%,\sDisk:\s(?P<disk>[\d.]+)%"
)

def parse_log():
    data = []
    try:
        with open(LOG_FILE, "r") as f:
            for line in f:
                match = log_pattern.search(line)
                if not match:
                    continue
                try:
                    ts = datetime.strptime(match.group("time"), "%Y-%m-%d %H:%M:%S")
                    cpu = float(match.group("cpu"))
                    mem = float(match.group("memory"))
                    disk = float(match.group("disk"))
                    temps = eval(match.group("temps"))  # Assuming dict of core temps
                    avg_temp = sum(temps.values()) / len(temps) if temps else 0.0

                    data.append({
                        "Time": ts,
                        "CPU": cpu,
                        "Memory": mem,
                        "Disk": disk,
                        "Temp": avg_temp
                    })
                except Exception:
                    continue
    except FileNotFoundError:
        pass
    return pd.DataFrame(data)

# --------------------------
# Gauge Drawing
# --------------------------

last_values = {}

def draw_gauge(canvas, label, value, min_val, max_val):
    canvas.delete("all")
    size = 200
    center = size // 2
    radius = 70

    canvas.create_oval(center - radius, center - radius, center + radius, center + radius, outline=FG_COLOR, width=3)

    for i in range(13): 
        angle_deg = (i / 12) * 360 - 90
        angle_rad = math.radians(angle_deg)
        length = 10 if i % 3 == 0 else 5
        inner = radius - length

        x1 = center + inner * math.cos(angle_rad)
        y1 = center + inner * math.sin(angle_rad)
        x2 = center + radius * math.cos(angle_rad)
        y2 = center + radius * math.sin(angle_rad)
        canvas.create_line(x1, y1, x2, y2, fill=FG_COLOR, width=2)

        if i % 3 == 0:
            pct = int((i / 12) * 100)
            lx = center + (radius + 15) * math.cos(angle_rad)
            ly = center + (radius + 15) * math.sin(angle_rad)
            canvas.create_text(lx, ly, text=f"{pct}%", fill=FG_COLOR, font=("Courier", 8, "bold"))

    angle = (value / 100) * 360 - 90
    needle_x = center + radius * 0.75 * math.cos(math.radians(angle))
    needle_y = center + radius * 0.75 * math.sin(math.radians(angle))
    canvas.create_line(center, center, needle_x, needle_y, fill="red", width=3)

    canvas.create_text(center, center, text=f"{value:.1f}%", fill=FG_COLOR, font=("Courier", 12, "bold"))

    canvas.create_text(center, 15, text=label, fill=FG_COLOR, font=("Courier", 14, "bold"))
    canvas.create_text(center, center + radius + 35, text=f"↓ {min_val:.1f}%   ↑ {max_val:.1f}%", fill=FG_COLOR, font=("Courier", 11))

def animate_gauge(canvas, label, start, end, min_val, max_val, step=0):
    steps = 10
    duration = 500
    delay = duration // steps
    value = start + (end - start) * (step / steps)
    draw_gauge(canvas, label, value, min_val, max_val)

    if step < steps:
        canvas.after(delay, lambda: animate_gauge(canvas, label, start, end, min_val, max_val, step + 1))

# --------------------------
# Updating the UI
# --------------------------

def update_dashboard(canvases):
    df = parse_log()
    if df.empty:
        root.after(1000, lambda: update_dashboard(canvases))
        return

    for metric, canvas in canvases.items():
        if not settings["metrics"].get(metric, False):
            canvas.delete("all")
            continue

        series = df[metric]
        current = series.iloc[-1]
        min_val = series.min()
        max_val = series.max()
        prev_val = last_values.get(metric, current)

        animate_gauge(canvas, metric, prev_val, current, min_val, max_val)
        last_values[metric] = current

    root.after(1000, lambda: update_dashboard(canvases))

# --------------------------
# Main UI Function
# --------------------------

def main():
    global root
    root = tk.Tk()
    root.title("Live System Stats Gauges")
    root.configure(bg=BG_COLOR)
    root.geometry("1000x400")
    root.resizable(False, False)

    frame = tk.Frame(root, bg=BG_COLOR)
    frame.pack(expand=True)

    metrics_to_show = [m for m in ["CPU", "Memory", "Disk", "Temp"] if settings["metrics"].get(m, False)]
    canvases = {}

    for i, metric in enumerate(metrics_to_show):
        canvas = Canvas(frame, width=200, height=300, bg=BG_COLOR, highlightthickness=0)
        canvas.grid(row=0, column=i, padx=20, pady=10)
        canvases[metric] = canvas

    update_dashboard(canvases)
    root.mainloop()

# --------------------------
# Run
# --------------------------

if __name__ == "__main__":
    main()
