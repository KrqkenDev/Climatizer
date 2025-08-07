import tkinter as tk
from tkinter import colorchooser, messagebox
import json
import os

CONFIG_FILE = "settings.json"

DEFAULT_CONFIG = {
    "metrics": {
        "CPU": True,
        "Memory": True,
        "Disk": True,
        "Temp": True
    },
    "colors": {
        "bg": "#000000",
        "fg": "#FFFFFF"
    }
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def choose_color(key):
    current = config["colors"][key]
    new_color = colorchooser.askcolor(initialcolor=current)[1]
    if new_color:
        config["colors"][key] = new_color
        update_colors()

def update_colors():
    bg = config["colors"]["bg"]
    fg = config["colors"]["fg"]
    root.configure(bg=bg)

    for widget in root.winfo_children():
        if isinstance(widget, (tk.Label, tk.Button, tk.Checkbutton, tk.Frame)):
            try:
                widget.configure(bg=bg, fg=fg)
            except:
                pass

    for btn in color_buttons.values():
        key = 'bg' if btn['text'] == 'Background' else 'fg'
        btn.configure(bg=config["colors"][key], fg=fg if key == 'bg' else bg)

    save_btn.configure(bg=bg, fg=fg, activebackground=fg, activeforeground=bg)

def save_settings():
    for metric, var in metric_vars.items():
        config["metrics"][metric] = bool(var.get())

    save_config(config)
    messagebox.showinfo("Settings", "Configuration saved successfully.")
    root.destroy()

# ----------------------------
# Build UI
# ----------------------------

config = load_config()
bg = config["colors"]["bg"]
fg = config["colors"]["fg"]

root = tk.Tk()
root.title("⚙️ Settings")
root.geometry("320x450")  
root.resizable(False, False)
root.configure(bg=bg)

tk.Label(root, text="Select Metrics", font=("Courier", 14, "bold"), bg=bg, fg=fg).pack(pady=(10, 5))

# --- Metric Checkboxes ---
metric_frame = tk.Frame(root, bg=bg)
metric_frame.pack(pady=5)

metric_vars = {}
for metric in ["CPU", "Memory", "Disk", "Temp"]:
    var = tk.IntVar(value=int(config["metrics"].get(metric, False)))
    chk = tk.Checkbutton(
        metric_frame, text=metric, variable=var,
        bg=bg, fg=fg, font=("Courier", 12),
        activebackground=bg, activeforeground=fg,
        selectcolor=bg
    )
    chk.pack(anchor="w", pady=2)
    metric_vars[metric] = var

# --- Color Choosers ---
tk.Label(root, text="Colors", font=("Courier", 14, "bold"), bg=bg, fg=fg).pack(pady=(20, 5))

color_frame = tk.Frame(root, bg=bg)
color_frame.pack(pady=5)

color_buttons = {}
for key, label in [("bg", "Background"), ("fg", "Foreground")]:
    btn = tk.Button(
        color_frame, text=label,
        bg=config["colors"][key],
        fg=fg if key == "bg" else bg,
        font=("Courier", 12),
        width=15,
        command=lambda k=key: choose_color(k)
    )
    btn.pack(pady=5)
    color_buttons[key] = btn

# --- Save Button  ---
save_btn = tk.Button(
    root, text=" Save Settings",
    command=save_settings,
    font=("Courier", 12, "bold"),
    bg=bg, fg=fg,
    activebackground=fg, activeforeground=bg
)
save_btn.pack(pady=(30, 15), fill="x", padx=20)

# --- Launch ---
root.mainloop()
