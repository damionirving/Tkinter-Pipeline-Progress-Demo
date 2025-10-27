# Tkinter Pipeline Progress Demo

This project shows a clean pattern for running a long task (`pipeline.py`) in a background thread while safely streaming progress updates to a Tkinter GUI (`gui.py`) via a callable class (`ProgressHandler`).

---

## 1) Program Flow & How Files Interact

**Files**
- `gui.py` — Tkinter app entry point. Owns the main thread and UI widgets.
- `progress_handler.py` — Defines `ProgressHandler`, a *callable* class that transports progress from a worker thread to the GUI using a thread-safe queue and Tk’s `after()` polling.
- `pipeline.py` — The worker. Exposes `main(on_progress)` and repeatedly calls `on_progress(pct)` while doing work.

**Sequence**
```
User clicks "Start" in GUI
       │
       ▼
gui.py creates ProgressHandler(handler) bound to a widget
       │
       ├─ gui.py calls handler.poll(on_update=...)  # starts Tk 'after' loop
       │
       └─ gui.py starts a Thread(target=run_pipeline, args=(handler,))
                      │
                      ▼
                pipeline.main(on_progress=handler)
                      │
                      ├─ does work in background thread
                      ├─ calls handler(pct) repeatedly
                      │      (this executes ProgressHandler.__call__)
                      │      -> enqueues pct in a Queue
                      │
                      └─ returns "pipeline complete"
       ▲
       │
ProgressHandler.poll (in main/UI thread) runs via Tk.after
- drains Queue
- updates widgets via on_update(pct)
- when pct >= 100, marks done and can trigger on_result
```

**Key rules**
- Only the **main thread** may touch Tk widgets.
- The **worker thread** reports progress by calling the handler object; it never calls Tk APIs.
- `ProgressHandler.poll()` bridges threads: it pulls from the queue and updates UI safely using `after()`.

---

## 2) Set up Python (non‑Conda) and Virtual Environment

These steps assume you have a standard Python installation.

### Windows (PowerShell)
```powershell
python --version
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install pyinstaller
```

> If activation is blocked: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

### macOS / Linux
```bash
python3 --version
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pyinstaller
```

> Linux note: you might need `sudo apt-get install python3-tk` (or distro equivalent).

---

## 3) Run the GUI from source

Activate the venv, then:
```bash
python gui.py
```
Click **Start**. The progress bar and percentage label update live; when reaching 100%, the button re-enables and status shows completion.

---

## 4) Build a Standalone Executable with PyInstaller

### Direct build (no spec yet)
**Windows paths:**
```bash
pyinstaller --noconsole --onefile --name PipelineGUI --collect-all tkinter --distpath exe_out\dist --workpath exe_outuild gui.py
```

**macOS/Linux paths:**
```bash
pyinstaller --noconsole --onefile --name PipelineGUI --collect-all tkinter --distpath exe_out/dist --workpath exe_out/build gui.py
```

- `--noconsole` hides console window (Windows GUI app)
- `--onefile` packs into a single binary
- `--name PipelineGUI` sets app name
- `--collect-all tkinter` bundles Tk/ttk resources
- `--distpath`/`--workpath` choose output folders
- Entry point: `gui.py`

Resulting executable:
```
exe_out/dist/PipelineGUI.exe    (Windows)
exe_out/dist/PipelineGUI        (macOS/Linux)
```

### Building from a `.spec` file
First run generates `PipelineGUI.spec`. Edit it if needed (datas, hiddenimports, icon). Rebuild from the spec:
```bash
pyinstaller PipelineGUI.spec --distpath exe_out\dist --workpath exe_outuild
```
On macOS/Linux, use `/` instead of `\` for paths.

---

## 5) Project Layout

```
.
├── gui.py                 # Tkinter GUI (main application & threading control)
├── pipeline.py            # Worker logic; calls on_progress(pct)
├── progress_handler.py    # Callable progress bridge (Queue + Tk.after polling)
├── README.md              # This file
└── .gitignore             # Git ignore rules
```

---

## 6) Extending the Pattern

- Replace the simulated loop in `pipeline.py` with real tasks (I/O, CPU, network).
- Add cancel/pause/resume by letting `ProgressHandler` hold flags/events.
- Track multi-stage pipelines by emitting structured messages (e.g., dicts `{stage, pct, note}`) instead of raw ints.
- Swap the UI target: the same worker can report to CLI, web sockets, or logs just by passing a different callable.

---

## 7) Troubleshooting

- **GUI freezes** → ensure *no* Tk calls occur in the worker thread.
- **No progress** → verify `handler.poll(...)` is started and `pipeline.main(handler)` is used.
- **Missing Tk resources in build** → keep `--collect-all tkinter` or add datas in the spec.
- **Activation issues on Windows** → adjust execution policy as noted.

---

## 8) AI Project Recreation Prompt

If you ever need to recreate or extend this entire project using an AI model such as ChatGPT, use this prompt:

> **Prompt:**  
> You are an expert Python and Tkinter developer. I have a zipped project containing a Tkinter GUI that runs a background worker (`pipeline.py`) and reports progress using a callable class (`ProgressHandler`).  
>  
> I want you to:
> 1. **Unpack** the provided ZIP archive and inspect its structure and code.  
> 2. **Explain** how the project works — the flow between `gui.py`, `pipeline.py`, and `progress_handler.py`.  
> 3. **Rebuild or extend** the project in a new directory named `tk_pipeline_gui`.  
> 4. Ensure it uses **modern Python 3 syntax**, `venv`, and best practices for threading and Tkinter.  
> 5. Include the following files:
>    - `gui.py`: main Tkinter interface that runs the pipeline in a thread and shows progress.  
>    - `pipeline.py`: background task that calls a progress callback.  
>    - `progress_handler.py`: callable class that queues progress and updates Tkinter safely.  
>    - `.gitignore`: Python defaults plus venv and build folders.  
>    - `README.md`: detailed documentation explaining installation, venv setup (non-Conda), execution, and building an `.exe` using PyInstaller.  
> 6. Add a **section in the README** that documents full program flow, showing how each script interacts, and include the PyInstaller command:
>    ```bash
>    pyinstaller --noconsole --onefile --name PipelineGUI --collect-all tkinter --distpath exe_out\dist --workpath exe_out\build gui.py
>    ```
> 7. Ensure the project can be run with:
>    ```bash
>    python gui.py
>    ```
>    and built into a standalone executable on Windows or macOS.  
> 8. Output the final project as a downloadable `.zip` archive.

---

## License

Public domain / Unlicense.
