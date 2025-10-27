# progress_handler.py
# A callable class that shuttles progress from a worker thread to Tkinter's main thread.

from queue import Queue, Empty

class ProgressHandler:
    def __init__(self, widget, poll_ms: int = 50):
        """Create a handler bound to a Tkinter widget.

        Args:
            widget: A Tk widget (e.g., Label, Progressbar) whose .after(...) we can call
            poll_ms: How often to poll the internal queue (milliseconds)
        """
        self.widget = widget
        self.queue = Queue()
        self.last_value = 0
        self.done = False
        self.poll_ms = poll_ms
        self._on_result = None  # optional callback when done

    def set_on_result(self, fn):
        """Optional: set a callback called on completion with the last value/result."""
        self._on_result = fn

    def __call__(self, pct: int):
        """Called by the worker thread to enqueue progress safely."""
        self.queue.put(pct)

    def poll(self, on_update=None):
        """Poll the queue from the GUI thread and update UI.

        Args:
            on_update: optional function receiving the new pct for custom UI updates.
        """
        try:
            while True:
                msg = self.queue.get_nowait()
                self.last_value = int(msg)
                if on_update is not None:
                    on_update(self.last_value)
                # mark completion if >=100 (convention)
                if self.last_value >= 100:
                    self.done = True
                    if self._on_result:
                        try:
                            self._on_result(self.last_value)
                        except Exception:
                            pass
        except Empty:
            pass
        # schedule another poll
        self.widget.after(self.poll_ms, lambda: self.poll(on_update))
