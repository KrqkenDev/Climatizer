import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import json

# ----------------------------
# Config
# ----------------------------
CONFIG_FILE = "settings.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "metrics": {"CPU": True, "Memory": True, "Disk": True, "Temp": True},
        "colors": {"bg": "#000000", "fg": "#FFFFFF"}
    }

config = load_config()
BG_COLOR = config["colors"]["bg"]
FG_COLOR = config["colors"]["fg"]

# paths
MAIN_SCRIPT = "logger.py"
GRAPH_SCRIPT = "graph.py"
SETTINGS_SCRIPT = "settings.py"
STATS_SCRIPT = "stats.py"

subprocesses = []
main_started = False

FONT = ("Courier", 20)

# ----------------------------
# Functions
# ----------------------------

def launch_script(script_name):
    if os.path.exists(script_name):
        try:
            proc = subprocess.Popen(["python", script_name])
            subprocesses.append(proc)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start {script_name}\n{e}")
    else:
        messagebox.showerror("Error", f"Script not found:\n{script_name}")

def start_main_script():
    global main_started
    if not main_started:
        if os.path.exists(MAIN_SCRIPT):
            proc = subprocess.Popen(["python", MAIN_SCRIPT])
            subprocesses.append(proc)
            main_started = True
            show_feature_buttons()
            start_button.pack_forget()
            title_label.pack_forget()
        else:
            messagebox.showerror("Error", f"{MAIN_SCRIPT} not found.")

def show_feature_buttons():
    button_frame = tk.Frame(root, bg=BG_COLOR)
    button_frame.place(relx=0.5, rely=0.5, anchor="center")

    row = 0

    if any(config["metrics"].values()):
        stats_btn = tk.Button(button_frame, text="Stats", font=FONT,
                              bg=BG_COLOR, fg=FG_COLOR,
                              activebackground=FG_COLOR, activeforeground=BG_COLOR,
                              width=20, height=2,
                              command=lambda: launch_script(STATS_SCRIPT))
        stats_btn.grid(row=row, column=0, padx=10, pady=10)
    
    graph_btn = tk.Button(button_frame, text="Graphs", font=FONT,
                          bg=BG_COLOR, fg=FG_COLOR,
                          activebackground=FG_COLOR, activeforeground=BG_COLOR,
                          width=20, height=2,
                          command=lambda: launch_script(GRAPH_SCRIPT))
    graph_btn.grid(row=row, column=1, padx=10, pady=10)

    row += 1

    settings_btn = tk.Button(button_frame, text="Settings", font=FONT,
                             bg=BG_COLOR, fg=FG_COLOR,
                             activebackground=FG_COLOR, activeforeground=BG_COLOR,
                             width=43, height=2,
                             command=lambda: launch_script(SETTINGS_SCRIPT))
    settings_btn.grid(row=row, column=0, columnspan=2, pady=10)

    row += 1

    exit_btn = tk.Button(button_frame, text="Exit", font=FONT,
                         bg="#8B0000", fg=FG_COLOR,
                         activebackground="#B22222", activeforeground=FG_COLOR,
                         width=43, height=2,
                         command=on_close)
    exit_btn.grid(row=row, column=0, columnspan=2, pady=20)

def on_close():
    for proc in subprocesses:
        try:
            proc.terminate()
        except Exception as e:
            print(f"Could not terminate a process: {e}")
    root.destroy()

# ----------------------------
# UI Setup
# ----------------------------

def create_ui():
    global root, start_button, title_label

    root = tk.Tk()
    root.title("System Monitor")
    root.geometry("800x600")
    root.configure(bg=BG_COLOR)
    root.resizable(False, False)
    root.protocol("WM_DELETE_WINDOW", on_close)

    center_frame = tk.Frame(root, bg=BG_COLOR)
    center_frame.place(relx=0.5, rely=0.5, anchor="center")

    title_label = tk.Label(center_frame, text="SYSTEM MONITOR", font=FONT,
                           bg=BG_COLOR, fg=FG_COLOR)
    title_label.pack(pady=20)

    start_button = tk.Button(center_frame, text="Start System Monitoring",
                             font=FONT,
                             bg=BG_COLOR, fg=FG_COLOR,
                             activebackground=FG_COLOR, activeforeground=BG_COLOR,
                             width=30, height=2,
                             command=start_main_script)
    start_button.pack(pady=10)

    root.mainloop()

# ----------------------------
# Run
# ----------------------------

if __name__ == "__main__":
    create_ui()
