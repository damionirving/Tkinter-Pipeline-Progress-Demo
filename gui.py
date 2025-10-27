# gui.py
# Tkinter GUI that imports pipeline.py (worker) and ProgressHandler.

#=============================================================================================================================
# NEW BUILD LOCATION
# pyinstaller --noconsole --onefile --name PipelineGUI --collect-all tkinter --distpath exe_out\dist --workpath exe_out\build gui.py

#=============================================================================================================================


import tkinter as tk
from threading import Thread
from tkinter import ttk
from pipeline import main as run_pipeline
from progress_handler import ProgressHandler

def build_ui(root):
    root.title("Pipeline Progress Demo")
    root.geometry("360x160")

    title = tk.Label(root, text="Running pipeline...", font=("Arial", 12))
    title.pack(pady=(12, 6))

    pct_var = tk.StringVar(value="0%")

    # Progress bar
    pb = ttk.Progressbar(root, orient="horizontal", length=280, mode="determinate", maximum=100)
    pb.pack(pady=6)

    # Percentage label
    pct_label = tk.Label(root, textvariable=pct_var, font=("Arial", 11))
    pct_label.pack(pady=2)

    # Start button
    btn = ttk.Button(root, text="Start", command=lambda: start_job(pct_label, pb, pct_var, btn))
    btn.pack(pady=8)

def start_job(pct_label, pb, pct_var, btn):
    btn.config(state=tk.DISABLED)

    # Create a handler bound to any widget that can call .after (label works fine)
    handler = ProgressHandler(pct_label, poll_ms=50)

    # Optional: what to do when complete
    def on_done(_last):
        pct_var.set("Done!")
        btn.config(state=tk.NORMAL)

    handler.set_on_result(on_done)

    # Define how GUI updates on each pct
    def update_ui(pct: int):
        pct = max(0, min(100, pct))
        pct_var.set(f"{pct}%")
        pb['value'] = pct

    # start polling for updates
    handler.poll(on_update=update_ui)

    # background thread to run pipeline
    def worker():
        res = run_pipeline(handler)  # pass the object like a function
        # If you need final result text displayed, you can enqueue it or rely on on_done
        # For demo, we don't need extra UI updates here.

    Thread(target=worker, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    # Some platforms need ttk theme initialized
    style = ttk.Style()
    try:
        style.theme_use(style.theme_use())
    except Exception:
        pass
    build_ui(root)
    root.mainloop()
